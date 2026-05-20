"""
Hosts 管线：拉取 → 聚合候选 → 延迟优选 → 历史兜底 → 写入 → iKuai 同步 → 通知
"""
import re
from datetime import datetime
from urllib.parse import urlparse

from app.config import config
from app.services.hosts_service import HostsService
from app.services.ikuai_service import IkuaiService
from app.services.notify_service import build_structured_notification, notify_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class HostsPipeline:
    """Hosts 更新管线"""

    def __init__(self):
        self._hosts = HostsService()

    @staticmethod
    def _tracker_to_hostname(tracker_url: str) -> str | None:
        """
        从 tracker URL 提取主机名
        udp://btn.track.com:1337/announce → btn.track.com
        http://tracker.example.com/announce → tracker.example.com
        """
        try:
            parsed = urlparse(tracker_url)
            if parsed.hostname:
                return parsed.hostname
            # fallback: 尝试正则
            m = re.match(r"^\w+://([^/:]+)", tracker_url)
            return m.group(1) if m else None
        except Exception:
            return None

    @staticmethod
    def _create_ikuai_service() -> IkuaiService | None:
        """按当前配置创建爱快服务实例"""
        if not config.get("ikuai.enabled", False):
            return None

        service = IkuaiService()
        service.init_config(
            host=config.get("ikuai.host", ""),
            port=None,
            username=config.get("ikuai.username", "admin"),
            password=config.get("ikuai.password", ""),
        )
        return service if service.is_enabled else None

    async def run(
        self,
        sources: list[dict],
        cf_ip_map: dict[str, str],
        clear_first: bool = False,
        notify_context: dict | None = None,
    ) -> dict:
        """
        执行完整 Hosts 管线
        1. 拉取所有源并聚合同域名候选 IP（仅 Managed Hosts 源）
        2. 单独整理 CF Tracker 映射
        3. 对 Managed Hosts 源候选 IP 做最小可用延迟优选
        4. 用当前 Managed Hosts / 最近成功历史补回本轮缺失域名
        5. 将 PT-Tracker 与 Managed Hosts 源两个独立分区合并写入 Hosts 文件
        6. 同步 iKuai（可选）
        7. 发送通知
        """
        logger.info("=== Hosts 管线开始 ===")
        result = {
            "success": True,
            "merged_count": 0,
            "candidate_domain_count": 0,
            "candidate_ip_count": 0,
            "latency_probe_success_count": 0,
            "latency_probe_fallback_count": 0,
            "latency_probe_fallback_domains": [],
            "history_fallback_count": 0,
            "cf_count": 0,
            "ikuai_synced": False,
            "ikuai_sync_count": 0,
            "errors": [],
        }

        try:
            if clear_first:
                self._hosts.clear_project_blocks()

            # Step 1: 拉取所有源并保留同域名的全部候选 IP（仅 Managed Hosts 源）
            managed_candidates: dict[str, set[str]] = {}
            enabled_sources = [source for source in sources if source.get("enabled", True)]
            source_fetch_success_count = 0

            active_domains = set()
            cached_source_domains = self._hosts.load_source_domains()

            for source in enabled_sources:
                source_id = source.get("id")
                source_name = source.get("name") or source_id or source.get("url", "未知源")
                source_url = source.get("url", "")
                try:
                    content = await self._hosts.fetch_source(source_url)
                    parsed = self._hosts.parse_hosts_candidates(content)
                    managed_candidates = self._hosts.add_candidates(managed_candidates, parsed)

                    # 记录并保存该源本次成功拉取的所有域名
                    fetched_domains = list(parsed.keys())
                    active_domains.update(fetched_domains)
                    if source_id:
                        self._hosts.save_source_domains(source_id, fetched_domains)

                    source_fetch_success_count += 1
                except Exception as e:
                    error_message = f"Hosts 源拉取失败：{source_name}（{source_url}） - {type(e).__name__}: {e}"
                    result["errors"].append(error_message)
                    logger.warning(error_message, exc_info=True)

                    # 拉取失败时，如果本地有该源的历史缓存域名，则加载作为活跃域名参与历史兜底
                    if source_id and source_id in cached_source_domains:
                        active_domains.update(cached_source_domains[source_id])

            # Step 2: 单独整理 CF Tracker 映射（tracker URL → hostname 作为域名）
            cf_hosts: list[dict] = []
            cf_mapping: dict[str, str] = {}
            for tracker_url, ip in cf_ip_map.items():
                hostname = self._tracker_to_hostname(tracker_url)
                if hostname:
                    cf_mapping[hostname] = ip
                    cf_hosts.append({"domain": hostname, "ip": ip})
            result["cf_count"] = len(cf_hosts)

            candidate_ip_count = sum(len(ips) for ips in managed_candidates.values())
            result["candidate_domain_count"] = len(managed_candidates)
            result["candidate_ip_count"] = candidate_ip_count
            logger.info(
                f"Managed Hosts 候选已聚合：{len(managed_candidates)} 个域名，{candidate_ip_count} 个候选 IP（来源成功 {source_fetch_success_count}/{len(enabled_sources)}，Tracker 独立分区：{len(cf_hosts)}）"
            )

            # Step 3: 仅对 Managed Hosts 源做最小可用延迟优选；全部失败时兜底到稳定首个候选 IP
            managed_mapping, selection_details = await self._hosts.select_best_candidates(managed_candidates)
            result["latency_probe_success_count"] = sum(
                1 for detail in selection_details.values()
                if detail.get("strategy") == "latency_probe"
            )
            result["latency_probe_fallback_count"] = sum(
                1 for detail in selection_details.values()
                if detail.get("strategy") == "fallback_first_candidate"
            )
            result["latency_probe_fallback_domains"] = sorted([
                domain for domain, detail in selection_details.items()
                if detail.get("strategy") == "fallback_first_candidate"
            ])

            # Step 4: 用当前 Managed Hosts / 最近成功历史补回本轮缺失域名（过滤已关闭或已删除源的域名）
            managed_mapping, history_fallback_details = self._hosts.apply_history_fallback(
                managed_mapping,
                excluded_domains=set(cf_mapping.keys()),
                active_domains=active_domains,
            )

            result["history_fallback_count"] = len(history_fallback_details)
            result["merged_count"] = len(managed_mapping)
            logger.info(
                f"Managed Hosts 延迟优选完成：{len(managed_mapping)} 条最终记录，探测成功 {result['latency_probe_success_count']} 条，探测失败兜底 {result['latency_probe_fallback_count']} 条，历史补回 {result['history_fallback_count']} 条；PT-Tracker 分区 {len(cf_mapping)} 条独立写入"
            )

            # Step 5: 将两个独立分区合并写入 Hosts 文件，并仅为 Managed Hosts 刷新历史
            self._hosts.write_hosts(managed_mapping, tracker_mapping=cf_mapping)
            self._hosts.save_history_ips(managed_mapping)

            # Step 6: iKuai 同步（仅同步 CFST 生成的 tracker 记录）
            service = self._create_ikuai_service()
            if service:
                try:
                    result["ikuai_synced"] = service.sync_hosts_to_dns(cf_hosts)
                    result["ikuai_sync_count"] = len(cf_hosts) if result["ikuai_synced"] else 0
                    if result["ikuai_synced"]:
                        logger.info(f"iKuai DNS 同步完成：{len(cf_hosts)} 条记录")
                    else:
                        result["errors"].append("iKuai DNS 同步失败")
                finally:
                    service.close()

            # Step 7: 发送通知
            self._send_notification(result=result, notify_context=notify_context)

        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
            logger.error(f"Hosts 管线异常：{type(e).__name__}: {e}", exc_info=True)

        logger.info("=== Hosts 管线完成 ===")
        return result

    def _send_notification(self, result: dict, notify_context: dict | None = None):
        """发送 Hosts / 联动通知"""
        try:
            total_hosts_count = int(result.get("merged_count", 0)) + int(result.get("cf_count", 0))
            success = bool(result.get("success", False)) and not result.get("errors")

            if notify_context:
                fallback_domains = result.get("latency_probe_fallback_domains", [])
                push_time = datetime.now()
                fallback_domain_lines = ["• 失败兜底域名："]
                if fallback_domains:
                    fallback_domain_lines.extend([f"      - {domain}" for domain in fallback_domains])
                else:
                    fallback_domain_lines = ["• 失败兜底域名：0"]

                lines = [
                    "──────────",
                    "📌 任务类型：IP优选与Hosts更新",
                    f"{'✅' if success else '❌'} 执行结果：{'任务完成' if success else '任务失败'}",
                    "──────────",
                    "🎯 优选结果：",
                    f"• 旧 IP：{notify_context.get('old_ip') or '未知'}",
                    f"• 新 IP：{notify_context.get('new_ip') or '未知'}",
                    f"• 测速耗时：{float(notify_context.get('duration_seconds', 0.0)):.2f} 秒",
                    f"• Tracker 更新数：{notify_context.get('tracker_update_count', 0)}",
                    f"• Hosts 记录数：{total_hosts_count}",
                    "──────────",
                    "📋 Hosts源统计：",
                    f"• 探测成功数：{result.get('latency_probe_success_count', 0)}",
                    f"• 失败兜底数：{result.get('latency_probe_fallback_count', 0)}",
                    *fallback_domain_lines,
                    "──────────",
                    f"⏰ 推送时间：{push_time.strftime('%Y-%m-%d %H:%M:%S')}",
                ]
                title = "【🚀 IP优选与Hosts更新】"
                message = "\n".join(lines)
            else:
                title, message = build_structured_notification(
                    header="Hosts更新",
                    task_type="Hosts更新",
                    success=success,
                    detail_title="更新结果",
                    detail_items=[
                        ("Hosts 记录数", total_hosts_count),
                        ("iKuai 同步数", result.get("ikuai_sync_count", 0)),
                        ("历史补回数", result.get("history_fallback_count", 0)),
                    ],
                    result_text="任务完成" if success else "任务失败",
                    push_time=datetime.now(),
                )

            notify_service.send(
                channel_id="default",
                title=title,
                message=message,
            )
        except Exception as e:
            logger.warning(f"发送通知失败：{e}")

