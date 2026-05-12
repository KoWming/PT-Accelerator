"""
Tracker 存储层。

职责：
- 从独立的 YAML 文件读取 / 保存 tracker 列表
- 首次读取时兼容旧版 config.trackers.items 并自动迁移
- 迁移完成后清空主配置中的 trackers.items，避免双写
"""
from __future__ import annotations

from pathlib import Path
from threading import Lock

import yaml

from app.config import CONFIG_DIR, config
from app.services.cloudflare_detector import cloudflare_detector
from app.utils.file_lock import file_lock
from app.utils.logger import get_logger

logger = get_logger(__name__)

TRACKERS_PATH = Path(CONFIG_DIR) / "trackers.yaml"
TRACKERS_LOCK_FILE = str(TRACKERS_PATH) + ".lock"
DEFAULT_TRACKERS_DATA = {"cloudflare_domains": [], "items": []}


class TrackerStore:
    """Tracker 独立存储。"""

    def __init__(self, path: Path = TRACKERS_PATH):
        self._path = path
        self._lock = Lock()

    def load_items(self) -> list[dict]:
        """加载 tracker 列表；必要时从旧配置迁移。"""
        return [self._copy_item(item) for item in self.load_data().get("items", [])]

    def load_cloudflare_domains(self) -> list[str]:
        """加载 Cloudflare 域名名单。"""
        return list(self.load_data().get("cloudflare_domains", []))

    def save_cloudflare_domains(self, domains: list[str]):
        """保存 Cloudflare 域名名单到独立文件。"""
        with self._lock:
            data = self._load_data_locked()
            data["cloudflare_domains"] = self._normalize_cloudflare_domains(domains)
            self._write_file(data)

    def load_data(self) -> dict:
        """加载完整 tracker 存储数据。"""
        with self._lock:
            data = self._load_data_locked()
            return {
                "cloudflare_domains": list(data.get("cloudflare_domains", [])),
                "items": [self._copy_item(item) for item in data.get("items", [])],
            }

    def save_items(self, items: list[dict]):
        """保存 tracker 列表到独立文件。"""
        with self._lock:
            data = self._load_data_locked()
            data["items"] = [self._copy_item(item) for item in items if isinstance(item, dict)]
            self._write_file(data)

    def _load_data_locked(self) -> dict:
        data = self._read_file()
        items = data.get("items")
        cloudflare_domains = data.get("cloudflare_domains")

        normalized_items = self._normalize_items(items if isinstance(items, list) else [])
        normalized_domains = self._normalize_cloudflare_domains(
            cloudflare_domains if isinstance(cloudflare_domains, list) else []
        )

        legacy_items = config.get("trackers.items", default=[])
        if isinstance(legacy_items, list) and legacy_items:
            logger.info(f"检测到旧版 Tracker 配置，开始迁移到独立文件：{self._path}")
            normalized_items = self._normalize_items(legacy_items)
            config.set("trackers.items", [])
            config.save()
            logger.info(f"Tracker 已迁移到独立文件：{self._path}")

        legacy_domains = config.get("cloudflare_domains", default=[])
        if isinstance(legacy_domains, str):
            legacy_domains = [legacy_domains]
        if isinstance(legacy_domains, list) and legacy_domains:
            migrated_domains = self._normalize_cloudflare_domains(legacy_domains)
            merged_domains = list(dict.fromkeys([*normalized_domains, *migrated_domains]))
            if merged_domains != normalized_domains:
                logger.info(f"检测到旧版 Cloudflare 域名名单，开始迁移到独立文件：{self._path}")
                normalized_domains = merged_domains
            config.delete("cloudflare_domains")
            config.save()

        normalized_data = {
            "cloudflare_domains": normalized_domains,
            "items": normalized_items,
        }

        if normalized_data != data or not self._path.exists():
            self._write_file(normalized_data)

        return normalized_data

    def _read_file(self) -> dict:
        if not self._path.exists():
            return DEFAULT_TRACKERS_DATA.copy()
        try:
            with self._path.open("r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            logger.error(f"解析 Tracker 存储文件失败：{e}，将按空列表处理")
            return DEFAULT_TRACKERS_DATA.copy()
        return loaded if isinstance(loaded, dict) else DEFAULT_TRACKERS_DATA.copy()

    def _write_file(self, data: dict):
        normalized_data = {
            "cloudflare_domains": self._normalize_cloudflare_domains(data.get("cloudflare_domains", [])),
            "items": self._normalize_items(data.get("items", [])),
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with file_lock(TRACKERS_LOCK_FILE):
            with self._path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(
                    normalized_data,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                )

    @staticmethod
    def _normalize_cloudflare_domains(domains: list[object]) -> list[str]:
        normalized: list[str] = []
        for domain in domains:
            normalized_domain = cloudflare_detector._normalize_domain(str(domain or ""))
            if normalized_domain and normalized_domain not in normalized:
                normalized.append(normalized_domain)
        return sorted(normalized)

    def _normalize_items(self, items: list[dict]) -> list[dict]:
        normalized_items: list[dict] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            normalized = self._normalize_item(item)
            if normalized:
                normalized_items.append(normalized)
        return normalized_items

    def _normalize_item(self, item: dict) -> dict:
        url = str(item.get("url", "")).strip()
        if not url:
            return {}

        is_cloudflare = item.get("is_cloudflare")
        if not isinstance(is_cloudflare, bool):
            detection = cloudflare_detector.detect(url)
            is_cloudflare = detection["is_cloudflare"]

        return {
            "id": str(item.get("id") or "").strip(),
            "enabled": bool(item.get("enabled", True)),
            "name": str(item.get("name") or "").strip(),
            "url": url,
            "ip": self._normalize_ip(item.get("ip")),
            "is_cloudflare": bool(is_cloudflare),
        }

    @staticmethod
    def _normalize_ip(value: object) -> str | None:
        text = str(value).strip() if value is not None else ""
        return text or None

    @staticmethod
    def _copy_item(item: dict) -> dict:
        return dict(item)


tracker_store = TrackerStore()



