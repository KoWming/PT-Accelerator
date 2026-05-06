"""
CFST 完整执行管线：测速 → 提取全局最优 IP → 展开 tracker IP 映射 → 回写 Tracker 当前 IP → 更新 Hosts → iKuai 同步 → 通知

当前业务语义：
- CFST 结果第一条有效记录就是本轮 Cloudflare 全局最优 IP
- `best_result` 表示这条第一名测速结果
- `best_ip` 表示从 `best_result` 提取出的全局最优 IP
- `ip_map` 不是再次优选，而是把 `best_ip` 展开为所有 Cloudflare tracker 共用的写入映射

CfstService API:
  - run() -> task_id (启动后台测速)
  - get_status() -> {"running": bool}
  - get_results() -> list[dict]
  - get_best_result() -> dict | None
"""
import threading
import time
from datetime import datetime

from app.config import config
from app.pipelines.hosts_pipeline import HostsPipeline
from app.services.cfst_service import cfst_service

from app.services.hosts_service import HostsService
from app.services.notify_service import build_structured_notification, notify_service
from app.services.tracker_service import tracker_service, _normalize_target
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CfstPipeline:
    """CFST 测速管线。"""

    def __init__(self):
        self._cfst = cfst_service
        self._hosts = HostsService()

    def run_in_background(self, trackers: list[str]) -> str:
        """后台启动完整 CFST 管线，并立即返回已提交的 CFST 任务 ID。"""
        task_id = self._cfst.run()

        worker = threading.Thread(
            target=self._continue_pipeline_after_cfst,
            args=(trackers, task_id),
            daemon=True,
            name=f"cfst-pipeline-{task_id}",
        )
        worker.start()
        logger.info(f"CFST 完整管线已在后台提交：{task_id}")
        return task_id

    def _continue_pipeline_after_cfst(self, trackers: list[str], task_id: str) -> dict:
        """在 CFST 已启动后继续执行等待、回写、Hosts 与通知流程。"""
        started_at = time.perf_counter()
        started_datetime = datetime.now()
        result = {
            "success": True,
            "task_id": task_id,
            "results": [],
            "best_result": None,
            "best_ip": None,
            "previous_ip": None,
            "duration_seconds": 0.0,
            "ip_map": {},
            "tracker_ip_updated": False,
            "tracker_ip_updated_count": 0,
            "hosts_updated": False,
            "hosts_result": None,
            "errors": [],
        }
        pending_hosts_pipeline: tuple[HostsPipeline, list[dict], dict[str, str], dict] | None = None

        try:
            logger.info(f"CFST 任务已启动: {task_id}")

            runtime_config = self._cfst.get_runtime_config()
            cfst_timeout = max(int(runtime_config.get("timeout_seconds", 300) or 300), 30)
            max_wait = cfst_timeout + 30
            waited = 0

            while waited < max_wait:
                status = self._cfst.get_status()
                if not status["running"]:
                    break
                time.sleep(2)
                waited += 2

            if waited >= max_wait:
                logger.warning("CFST 测速超时")
                result["errors"].append("CFST 测速等待超时")

            results = self._cfst.get_results()
            result["results"] = results
            logger.info(f"CFST 测速完成：{len(results)} 条结果")

            best_result = self._cfst.get_best_result()
            result["best_result"] = best_result
            best_ip = best_result.get("ip") if best_result else None
            result["best_ip"] = best_ip

            ip_map = self._build_ip_map(trackers=trackers, best_ip=best_ip)
            result["ip_map"] = ip_map

            if best_ip:
                logger.info(f"CFST 全局最优 IP：{best_ip}，已展开到 {len(ip_map)} 个 tracker")
            else:
                logger.warning("CFST 管线未提取到全局最优 IP")

            previous_ip = self._collect_previous_tracker_ip(trackers)
            result["previous_ip"] = previous_ip
            if best_ip and trackers:
                updated_count = tracker_service.update_trackers_ip_by_urls(trackers, best_ip)
                result["tracker_ip_updated_count"] = updated_count
                result["tracker_ip_updated"] = updated_count > 0
                logger.info(f"CFST 已回写 Tracker 当前 IP：{updated_count} 条，IP={best_ip}")

            sources = self._hosts.list_sources()
            enabled_sources = [source for source in sources if source.get("enabled", True)]
            auto_update_hosts = bool(config.get("hosts.auto_update", default=True))
            if ip_map and auto_update_hosts:
                hosts_pipeline = HostsPipeline()
                pending_hosts_pipeline = (
                    hosts_pipeline,
                    enabled_sources,
                    {tracker: data["ip"] for tracker, data in ip_map.items() if data.get("ip")},
                    {
                        "started_at": started_datetime,
                        "old_ip": result.get("previous_ip") or "未知",
                        "new_ip": result.get("best_ip") or "未知",
                        "duration_seconds": round(time.perf_counter() - started_at, 2),
                        "tracker_update_count": result.get("tracker_ip_updated_count", 0),
                    },
                )
                result["hosts_updated"] = None
                if enabled_sources:
                    logger.info(f"CFST 管线准备启动 Hosts 更新：启用源 {len(enabled_sources)} 个，tracker 映射 {len(ip_map)} 条")
                else:
                    logger.info(f"CFST 管线准备启动 Hosts 更新：未配置启用的 hosts 源，将仅写入 PT-Tracker 分区（tracker 映射 {len(ip_map)} 条）")
            elif not ip_map:
                logger.warning("CFST 管线跳过 Hosts 更新：没有可用的全局最优 IP")
            else:
                logger.info("CFST 管线跳过 Hosts 更新：hosts.auto_update 已关闭")

            if pending_hosts_pipeline is None:
                self._send_notification(len(results), success=result["success"])

        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
            logger.error(f"CFST 管线异常：{e}")

        result["duration_seconds"] = round(time.perf_counter() - started_at, 2)

        if pending_hosts_pipeline is not None:
            hosts_pipeline, enabled_sources, tracker_ip_map, notify_context = pending_hosts_pipeline
            self._run_hosts_pipeline_background(hosts_pipeline, enabled_sources, tracker_ip_map, notify_context)
            logger.info("Hosts 管线已在后台启动")

        return result


    @staticmethod
    def _build_ip_map(trackers: list[str], best_ip: str | None) -> dict[str, dict]:
        """将全局最优 IP 展开为所有 tracker 共用的写入映射。"""
        if not best_ip:
            return {}

        return {
            tracker: {
                "ip": best_ip,
                "source": "cfst_best_ip",
            }
            for tracker in trackers
        }

    @staticmethod
    def _collect_previous_tracker_ip(trackers: list[str]) -> str | None:
        """在批量回写前收集一个可展示的旧 IP。"""
        normalized_targets = {
            _normalize_target(url)
            for url in trackers
            if _normalize_target(url)
        }
        if not normalized_targets:
            return None

        for item in tracker_service.list_trackers():
            if _normalize_target(item.get("url", "")) not in normalized_targets:
                continue
            old_ip = (item.get("ip") or "").strip()
            if old_ip:
                return old_ip
        return None

    def run(self, trackers: list[str]) -> dict:
        """
        执行完整 CFST 管线
        1. 运行测速（等待完成）
        2. 提取 CFST 第一行全局最优 IP
        3. 将全局最优 IP 展开为 tracker 映射
        4. 回写对应 Tracker 的当前 IP 字段
        5. 更新 Hosts
        6. 同步 iKuai（可选）
        7. 发送通知

        返回结构约定：
        - success: 管线整体是否成功
        - task_id: 本次 CFST 任务 ID
        - results: CFST 原始测速结果列表
        - best_result: 第一条有效测速结果，即本轮全局最优结果
        - best_ip: 从 best_result 提取出的全局最优 IP
        - ip_map: 将 best_ip 展开后的 tracker -> ip 写入映射
        - tracker_ip_updated: 是否已成功回写 Tracker 当前 IP
        - tracker_ip_updated_count: 本轮成功回写的 Tracker 数量
        - hosts_updated: 是否已成功触发 Hosts 更新
        - hosts_result: HostsPipeline 的执行结果
        - errors: 本轮执行过程中记录的错误列表
        """
        logger.info("=== CFST 管线开始 ===")
        task_id = self._cfst.run()
        result = self._continue_pipeline_after_cfst(trackers, task_id)
        logger.info("=== CFST 管线完成 ===")
        return result


    @staticmethod
    def _run_hosts_pipeline_background(
        pipeline: HostsPipeline,
        sources: list[dict],
        cf_ip_map: dict[str, str],
        notify_context: dict,
    ):
        """在后台独立线程中执行 Hosts 管线，不阻塞调用者。"""
        import asyncio
        import threading

        def _target():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(pipeline.run(sources=sources, cf_ip_map=cf_ip_map, notify_context=notify_context))
            except Exception as e:
                logger.error(f"后台 Hosts 管线执行失败：{e}")
            finally:
                loop.close()

        t = threading.Thread(target=_target, daemon=True, name="hosts-pipeline-bg")
        t.start()

    def _send_notification(self, result_count: int, success: bool = True):
        """发送测速完成通知。"""
        try:
            title, message = build_structured_notification(
                header="CFST测速",
                task_type="CFST测速",
                success=success,
                detail_title="测速结果",
                detail_items=[
                    ("结果数", result_count),
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

