"""
Hosts 源拉取、CF IP 合并、文件写入
"""
import asyncio
import hashlib
import os
import re
import shutil
import time
import yaml
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx

from app.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HOSTS_HISTORY_PATH = Path(WORKSPACE_ROOT) / "config" / "hosts_history.yaml"



class HostsService:

    """Hosts 管理服务"""

    LEGACY_PROJECT_START_MARK = "# == PT-Accelerator START =="
    LEGACY_PROJECT_END_MARK = "# == PT-Accelerator END =="
    TRACKER_SECTION_START_MARK = "# == PT-Tracker START ==#"
    TRACKER_SECTION_END_MARK_TEMPLATE = "# == PT-Tracker END ({count} 条记录) ==#"
    SECTION_SEPARATOR = "###################################"
    MANAGED_SECTION_START_MARK = "# ===== Managed Hosts 源 START ===== #"
    MANAGED_SECTION_END_MARK_TEMPLATE = "# ===== Managed Hosts 源 END ({count} 条记录) ===== #"

    def __init__(self):
        pass

    # ==================== 源管理 ====================

    def list_sources(self) -> list[dict]:
        """列出所有 Hosts 源"""
        return config.get("hosts.sources", default=[])

    def get_source(self, source_id: str) -> Optional[dict]:
        """按 ID 获取单个源"""
        sources = self.list_sources()
        for s in sources:
            if s.get("id") == source_id:
                return s
        return None

    def _gen_source_id(self, url: str) -> str:
        """根据 URL 生成稳定短 ID（取 MD5 前 8 位）"""
        return hashlib.md5(url.encode()).hexdigest()[:8]

    def add_source(self, name: str, url: str, enabled: bool = True) -> dict:
        """
        新增 Hosts 源
        Returns: 新增的源（含 id）
        Raises: ValueError("duplicate") 如果 URL 重复
        Raises: ValueError("format") 如果 URL 格式无效
        """
        # URL 格式基本校验
        if not url.startswith(("http://", "https://", "ftp://")):
            raise ValueError("format", f"无效的 URL 格式: {url}")

        # 重复检查
        sources = self.list_sources()
        for s in sources:
            if s.get("url", "").lower() == url.lower():
                raise ValueError("duplicate", f"URL 已存在: {url}")

        new_source = {
            "id": self._gen_source_id(url),
            "enabled": enabled,
            "name": name,
            "url": url,
        }

        sources.append(new_source)
        config.set("hosts.sources", sources)
        config.save()
        logger.info(f"Hosts 源已添加：{name}（{url}）")
        return new_source

    def update_source(self, source_id: str, name: Optional[str] = None, url: Optional[str] = None, enabled: Optional[bool] = None) -> Optional[dict]:
        """
        更新 Hosts 源
        Returns: 更新后的源，None 如果不存在
        Raises: ValueError("duplicate") 如果新 URL 与其他源重复
        Raises: ValueError("format") 如果 URL 格式无效
        """
        sources = self.list_sources()
        updated = None
        found = False
        for i, s in enumerate(sources):
            if s.get("id") == source_id:
                found = True
                new_name = name if name is not None else s.get("name", "")
                new_url = url if url is not None else s.get("url", "")
                new_enabled = enabled if enabled is not None else s.get("enabled", True)

                # URL 格式校验
                if not new_url.startswith(("http://", "https://", "ftp://")):
                    raise ValueError("format", f"无效的 URL 格式: {new_url}")
                # URL 重复检查（排除自身）
                for j, other in enumerate(sources):
                    if i != j and other.get("url", "").lower() == new_url.lower():
                        raise ValueError("duplicate", f"URL 已存在: {new_url}")
                sources[i] = {**s, "name": new_name, "url": new_url, "enabled": new_enabled}
                updated = sources[i]
                break
        if not found:
            return None
        config.set("hosts.sources", sources)
        config.save()
        logger.info(f"Hosts 源已更新：{source_id}")
        return updated


    def delete_source(self, source_id: str) -> bool:
        """删除 Hosts 源，返回是否实际删除了"""
        sources = self.list_sources()
        original_len = len(sources)
        sources = [s for s in sources if s.get("id") != source_id]
        if len(sources) == original_len:
            return False
        config.set("hosts.sources", sources)
        config.save()
        logger.info(f"Hosts 源已删除：{source_id}")
        self.delete_source_domains_cache(source_id)
        return True

    # ==================== 内容操作 ====================

    async def fetch_source(self, url: str) -> str:
        """拉取单个 Hosts 源内容"""
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text

    def parse_hosts_content(self, content: str) -> dict[str, str]:
        """
        解析 Hosts 内容
        Returns: {域名: IP}
        """
        mapping: dict[str, str] = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = re.split(r"\s+", line)
            if len(parts) < 2:
                continue

            ip = parts[0]
            if not self._is_valid_ip(ip):
                continue

            for token in parts[1:]:
                if token.startswith("#"):
                    break
                domain = token.strip()
                if domain:
                    mapping[domain] = ip
        return mapping

    def parse_hosts_candidates(self, content: str) -> dict[str, set[str]]:
        """解析 Hosts 源内容，保留同域名的全部候选 IP。"""
        candidates: defaultdict[str, set[str]] = defaultdict(set)
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = re.split(r"\s+", line)
            if len(parts) < 2:
                continue

            ip = parts[0]
            if not self._is_valid_ip(ip):
                continue

            for token in parts[1:]:
                if token.startswith("#"):
                    break
                domain = token.strip()
                if domain:
                    candidates[domain].add(ip)
        return dict(candidates)

    def add_candidates(self, candidate_map: dict[str, set[str]], mapping: dict[str, str] | dict[str, set[str]]) -> dict[str, set[str]]:
        """将 Hosts 映射聚合到 domain -> set[ip] 候选集合。"""
        result: defaultdict[str, set[str]] = defaultdict(set)
        for domain, ips in candidate_map.items():
            result[domain].update(ips)

        for domain, value in mapping.items():
            if not domain:
                continue

            ips = value if isinstance(value, set) else {value}
            for ip in ips:
                if ip and self._is_valid_ip(ip):
                    result[domain].add(ip)

        return dict(result)


    def collapse_candidates(self, candidate_map: dict[str, set[str]]) -> dict[str, str]:
        """将候选集合临时收敛为单值映射，当前使用稳定排序后的首个 IP。"""
        collapsed: dict[str, str] = {}
        for domain, ips in candidate_map.items():
            valid_ips = sorted(ip for ip in ips if self._is_valid_ip(ip))
            if valid_ips:
                collapsed[domain] = valid_ips[0]
        return collapsed

    @staticmethod
    async def _probe_ip_latency(ip: str, port: int, timeout: float) -> float | None:
        """探测单个 IP 的 TCP 建连延迟，失败返回 None。"""
        start = time.perf_counter()
        writer = None
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host=ip, port=port),
                timeout=timeout,
            )
            return round((time.perf_counter() - start) * 1000, 2)
        except Exception:
            return None
        finally:
            if writer is not None:
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:
                    pass

    async def select_best_candidates(self, candidate_map: dict[str, set[str]]) -> tuple[dict[str, str], dict[str, dict]]:
        """按域名对候选 IP 做最小可用延迟优选，并返回兜底/探测详情。"""
        probe_port = int(config.get("hosts.probe_port", default=443))
        probe_timeout = float(config.get("hosts.probe_timeout_seconds", default=1.5))
        selected: dict[str, str] = {}
        details: dict[str, dict] = {}

        for domain, ips in candidate_map.items():
            valid_ips = sorted(ip for ip in ips if self._is_valid_ip(ip))
            if not valid_ips:
                continue

            probe_results: dict[str, float | None] = {}
            for ip in valid_ips:
                probe_results[ip] = await self._probe_ip_latency(ip=ip, port=probe_port, timeout=probe_timeout)

            successful_results = {
                ip: latency for ip, latency in probe_results.items()
                if latency is not None
            }

            if successful_results:
                best_ip = min(successful_results.items(), key=lambda item: (item[1], item[0]))[0]
                selected[domain] = best_ip
                details[domain] = {
                    "strategy": "latency_probe",
                    "selected_ip": best_ip,
                    "probes": probe_results,
                }
            else:
                fallback_ip = valid_ips[0]
                selected[domain] = fallback_ip
                details[domain] = {
                    "strategy": "fallback_first_candidate",
                    "selected_ip": fallback_ip,
                    "probes": probe_results,
                }

        return selected, details

    @staticmethod
    def _normalize_domain(domain: str) -> str:
        """清洗域名字符串，去掉历史脏数据里的行尾注释与多余空白。"""
        cleaned = str(domain or "").split("#", 1)[0].strip()
        if not cleaned or any(char.isspace() for char in cleaned):
            return ""
        return cleaned

    @staticmethod
    def _normalize_history_map(history: dict) -> dict[str, str]:
        normalized: dict[str, str] = {}
        for domain, ip in history.items():
            cleaned_domain = HostsService._normalize_domain(domain)
            if cleaned_domain and isinstance(ip, str) and HostsService._is_valid_ip(ip):
                normalized[cleaned_domain] = ip
        return normalized


    def _extract_history_payload(self, loaded: object) -> dict:
        """兼容读取新版带头字段和旧版裸字典格式的 Hosts 历史文件。"""
        if not isinstance(loaded, dict):
            return {}

        history_section = loaded.get("history")
        if isinstance(history_section, dict):
            return history_section

        return loaded

    def get_history_ips(self) -> dict[str, str]:
        """读取最近一次成功写入的域名 IP 历史。"""
        if HOSTS_HISTORY_PATH.exists():
            try:
                with HOSTS_HISTORY_PATH.open("r", encoding="utf-8") as f:
                    loaded = yaml.safe_load(f) or {}
                history_payload = self._extract_history_payload(loaded)
                if history_payload:
                    return self._normalize_history_map(history_payload)
            except Exception as e:
                logger.warning(f"读取 Hosts 历史文件失败：{e}")

        legacy_history = config.get("hosts.domain_ip_history", default={})
        if isinstance(legacy_history, dict) and legacy_history:
            normalized = self._normalize_history_map(legacy_history)
            if normalized:
                self.save_history_ips(normalized)
                return normalized
        return {}

    def load_source_domains(self) -> dict[str, list[str]]:
        """读取源 ID 到域名列表的缓存映射"""
        if HOSTS_HISTORY_PATH.exists():
            try:
                with HOSTS_HISTORY_PATH.open("r", encoding="utf-8") as f:
                    loaded = yaml.safe_load(f) or {}
                return loaded.get("source_domains", {})
            except Exception as e:
                logger.warning(f"读取 Hosts 历史中的源域名映射失败：{e}")
        return {}

    def save_source_domains(self, source_id: str, domains: list[str]):
        """持久化单个源的域名列表缓存"""
        try:
            loaded = {}
            if HOSTS_HISTORY_PATH.exists():
                with HOSTS_HISTORY_PATH.open("r", encoding="utf-8") as f:
                    loaded = yaml.safe_load(f) or {}
            
            source_domains = loaded.setdefault("source_domains", {})
            source_domains[source_id] = sorted(list(set(domains)))
            
            HOSTS_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
            with HOSTS_HISTORY_PATH.open("w", encoding="utf-8") as f:
                yaml.safe_dump(loaded, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        except Exception as e:
            logger.warning(f"保存 Hosts 源域名缓存失败：{e}")

    def delete_source_domains_cache(self, source_id: str):
        """删除指定源的域名缓存"""
        try:
            if not HOSTS_HISTORY_PATH.exists():
                return
            with HOSTS_HISTORY_PATH.open("r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f) or {}
            
            source_domains = loaded.get("source_domains", {})
            if source_id in source_domains:
                del source_domains[source_id]
                with HOSTS_HISTORY_PATH.open("w", encoding="utf-8") as f:
                    yaml.safe_dump(loaded, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        except Exception as e:
            logger.warning(f"删除 Hosts 源域名缓存失败：{e}")

    def save_history_ips(self, mapping: dict[str, str], excluded_domains: set[str] | None = None):
        """持久化最近一次成功写入的域名 IP 历史。"""
        excluded = set(excluded_domains or set())
        history = {
            domain: ip
            for domain, ip in mapping.items()
            if domain and domain not in excluded and ip and self._is_valid_ip(ip)
        }
        loaded = {}
        if HOSTS_HISTORY_PATH.exists():
            try:
                with HOSTS_HISTORY_PATH.open("r", encoding="utf-8") as f:
                    loaded = yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"读取 Hosts 历史文件失败：{e}")

        loaded["history"] = history
        HOSTS_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with HOSTS_HISTORY_PATH.open("w", encoding="utf-8") as f:
            yaml.safe_dump(loaded, f, allow_unicode=True, default_flow_style=False, sort_keys=False)



    def _extract_managed_section_content(self, content: str) -> str:

        """提取当前 hosts 中的 Managed Hosts 源分区原文。"""
        pattern = re.compile(
            r"# ===== Managed Hosts 源 START ===== #\r?\n(?P<body>.*?)\r?\n# ===== Managed Hosts 源 END \(\d+ 条记录\) ===== #",
            re.DOTALL,
        )
        match = pattern.search(content)
        if match:
            return match.group("body")

        if self.LEGACY_PROJECT_START_MARK in content and self.LEGACY_PROJECT_END_MARK in content:
            start_pos = content.find(self.LEGACY_PROJECT_START_MARK)
            end_pos = content.find(self.LEGACY_PROJECT_END_MARK, start_pos)
            if end_pos != -1:
                legacy_block = content[start_pos:end_pos]
                legacy_match = re.search(
                    r"# ===== PT-Accelerator Managed Hosts 开始 ===== #\r?\n(?P<body>.*?)\r?\n# ===== PT-Accelerator Managed Hosts 结束 \(\d+ 条记录\) ===== #",
                    legacy_block,
                    re.DOTALL,
                )
                if legacy_match:
                    return legacy_match.group("body")

        return ""

    def get_managed_hosts_mapping(self) -> dict[str, str]:
        """读取当前 hosts 文件里 Managed Hosts 源分区的域名映射。"""
        content = self.get_hosts_content()
        if not content:
            return {}
        managed_content = self._extract_managed_section_content(content)
        if not managed_content:
            return {}
        return self.parse_hosts_content(managed_content)

    def apply_history_fallback(
        self,
        selected_map: dict[str, str],
        excluded_domains: set[str] | None = None,
        active_domains: set[str] | None = None,
    ) -> tuple[dict[str, str], dict[str, dict]]:
        """为本轮缺失域名补入当前 Managed Hosts / 历史中的最近成功 IP。"""
        merged = selected_map.copy()
        fallback_details: dict[str, dict] = {}
        excluded = set(excluded_domains or set())

        current_hosts = {
            domain: ip for domain, ip in self.get_managed_hosts_mapping().items()
            if domain not in excluded and (active_domains is None or domain in active_domains)
        }
        history_hosts = {
            domain: ip for domain, ip in self.get_history_ips().items()
            if domain not in excluded and (active_domains is None or domain in active_domains)
        }
        fallback_sources = [current_hosts, history_hosts]

        previous_domains: set[str] = set()
        for source in fallback_sources:
            previous_domains.update(source.keys())

        missing_domains = sorted(domain for domain in previous_domains if domain not in merged)
        for domain in missing_domains:
            fallback_ip = None
            fallback_source = None
            for source_name, source_map in (("current_hosts", current_hosts), ("history", history_hosts)):
                ip = source_map.get(domain)
                if ip and self._is_valid_ip(ip):
                    fallback_ip = ip
                    fallback_source = source_name
                    break

            if fallback_ip:
                merged[domain] = fallback_ip
                fallback_details[domain] = {
                    "strategy": "history_fallback",
                    "selected_ip": fallback_ip,
                    "source": fallback_source,
                }

        return merged, fallback_details


    @staticmethod
    def _is_valid_ip(ip: str) -> bool:
        """简单 IPv4 校验"""
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        return all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)

    def merge_cf_ips(self, hosts_map: dict[str, str], cf_ip_map: dict[str, str]) -> dict[str, str]:
        """合并 CF IP 到 Hosts 映射（CF IP 优先级最高）"""
        result = hosts_map.copy()
        result.update(cf_ip_map)
        return result

    def get_hosts_path(self) -> str:
        """获取当前配置的 Hosts 文件路径"""
        return config.get("hosts.target_path",
                           default="C:\\Windows\\System32\\drivers\\etc\\hosts")

    def get_hosts_content(self) -> str:
        """读取当前 Hosts 文件内容"""
        hosts_path = self.get_hosts_path()
        if not os.path.exists(hosts_path):
            return ""
        try:
            with open(hosts_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取 hosts 文件失败：{e}")
            return ""

    def get_current_ips(self) -> list[dict]:
        """
        从当前 Hosts 文件中提取 tracker IP 映射
        Returns: [{tracker, ip, source, updated_at}]
        """
        content = self.get_hosts_content()
        if not content:
            return []
        mapping = self.parse_hosts_content(content)
        result = []
        mtime = os.path.getmtime(self.get_hosts_path()) if os.path.exists(self.get_hosts_path()) else None
        updated_at = datetime.fromtimestamp(mtime).isoformat() if mtime else None
        for tracker, ip in sorted(mapping.items()):
            result.append({
                "tracker": tracker,
                "ip": ip,
                "source": "local",
                "updated_at": updated_at,
            })
        return result

    def get_backup_enabled(self) -> bool:
        return config.get("hosts.backup_enabled", default=True)

    @staticmethod
    def _to_log_path(path: str) -> str:
        """日志中优先显示工作区相对路径。"""
        absolute_path = os.path.abspath(path)
        try:
            relative_path = os.path.relpath(absolute_path, WORKSPACE_ROOT)
            if not relative_path.startswith(".."):
                return relative_path.replace("/", "\\")
        except ValueError:
            pass
        return absolute_path




    def _render_tracker_lines(self, tracker_mapping: dict[str, str]) -> list[str]:
        """渲染 tracker 分区条目。"""
        return [f"{ip}\t{domain}" for domain, ip in sorted(tracker_mapping.items())]

    def _render_managed_lines(self, mapping: dict[str, str]) -> list[str]:
        """渲染合并后的 hosts 源分区条目。"""
        return [f"{ip}\t{domain}" for domain, ip in sorted(mapping.items())]

    def _render_project_block(self, tracker_mapping: dict[str, str], mapping: dict[str, str]) -> str:
        """渲染 PT-Tracker 与 Managed Hosts 源两个平级分区。"""
        tracker_lines = self._render_tracker_lines(tracker_mapping)
        managed_lines = self._render_managed_lines(mapping)

        lines: list[str] = []
        if tracker_lines:
            lines.append(self.TRACKER_SECTION_START_MARK)
            lines.extend(tracker_lines)
            lines.append(self.TRACKER_SECTION_END_MARK_TEMPLATE.format(count=len(tracker_lines)))

        if tracker_lines and managed_lines:
            lines.append(self.SECTION_SEPARATOR)

        if managed_lines:
            lines.append(self.MANAGED_SECTION_START_MARK)
            lines.extend(managed_lines)
            lines.append(self.MANAGED_SECTION_END_MARK_TEMPLATE.format(count=len(managed_lines)))

        return "\n".join(lines)

    def _strip_managed_block(self, content: str) -> str:

        """移除历史 PT 分区与当前新分区，保留其他系统内容。"""
        result = content
        while self.LEGACY_PROJECT_START_MARK in result and self.LEGACY_PROJECT_END_MARK in result:
            start_pos = result.find(self.LEGACY_PROJECT_START_MARK)
            end_pos = result.find(self.LEGACY_PROJECT_END_MARK, start_pos)
            if end_pos == -1:
                break
            end_pos += len(self.LEGACY_PROJECT_END_MARK)
            result = (result[:start_pos] + result[end_pos:]).strip("\r\n")

        # 先用贪婪模式一次性移除所有 PT-Tracker 块（避免非贪婪只清第一个）
        tracker_pattern = re.compile(
            r"(?:^|\r?\n)(# == PT-Tracker START ==.*?# == PT-Tracker END \(\d+ 条记录\) ==#)\r?\n?",
            re.DOTALL,
        )
        result = tracker_pattern.sub("", result)

        # 再清理 Managed Hosts 块和分隔线
        managed_pattern = re.compile(
            r"(?:^|\r?\n)(# ===== Managed Hosts 源 START ===== #.*?# ===== Managed Hosts 源 END \(\d+ 条记录\) ===== #)\r?\n?",
            re.DOTALL,
        )
        separator_pattern = re.compile(r"(?:^|\r?\n)?###################################(?:$|\r?\n)?")

        result = managed_pattern.sub("", result)
        result = separator_pattern.sub("\n", result)
        return result.strip("\r\n")




    def write_hosts(self, mapping: dict[str, str], tracker_mapping: dict[str, str] | None = None):
        """写入 Hosts 文件（带备份，仅替换 PT-Accelerator 管理分区）"""
        hosts_path = self.get_hosts_path()
        if self.get_backup_enabled() and os.path.exists(hosts_path):
            backup_path = hosts_path + ".bak"
            shutil.copy2(hosts_path, backup_path)
            logger.info(f"Hosts 备份已创建：{self._to_log_path(backup_path)}")

        existing_content = self.get_hosts_content()

        base_content = self._strip_managed_block(existing_content)
        tracker_mapping = tracker_mapping or {}
        tracker_domains = set(tracker_mapping.keys())
        managed_mapping = {
            domain: ip
            for domain, ip in mapping.items()
            if domain not in tracker_domains
        }
        managed_block = self._render_project_block(tracker_mapping, managed_mapping)

        if base_content.strip():
            content = base_content.rstrip() + "\n\n" + managed_block + "\n"
        else:
            content = managed_block + "\n"

        with open(hosts_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(
            f"Hosts 文件已写入管理分区：{self._to_log_path(hosts_path)}（tracker {len(tracker_mapping)} 条，managed hosts {len(managed_mapping)} 条）"
        )

    def clear_project_blocks(self):
        """清空当前 Hosts 文件中由项目写入的管理分区。"""
        hosts_path = self.get_hosts_path()
        existing_content = self.get_hosts_content()
        cleared_content = self._strip_managed_block(existing_content)

        if self.get_backup_enabled() and os.path.exists(hosts_path):
            backup_path = hosts_path + ".bak"
            shutil.copy2(hosts_path, backup_path)
            logger.info(f"Hosts 备份已创建：{self._to_log_path(backup_path)}")

        final_content = (cleared_content.rstrip() + "\n") if cleared_content.strip() else ""
        with open(hosts_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        logger.info(f"Hosts 文件中的项目管理分区已清空：{self._to_log_path(hosts_path)}")






    def write_hosts_content(self, content: str):
        """
        直接写入 Hosts 文件内容（带备份）
        """
        hosts_path = self.get_hosts_path()
        if self.get_backup_enabled() and os.path.exists(hosts_path):
            backup_path = hosts_path + ".bak"
            shutil.copy2(hosts_path, backup_path)
            logger.info(f"Hosts 备份已创建：{self._to_log_path(backup_path)}")

        with open(hosts_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Hosts 文件内容已直接写入：{self._to_log_path(hosts_path)}")






