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
DEFAULT_TRACKERS_DATA = {"items": []}


class TrackerStore:
    """Tracker 独立存储。"""

    def __init__(self, path: Path = TRACKERS_PATH):
        self._path = path
        self._lock = Lock()

    def load_items(self) -> list[dict]:
        """加载 tracker 列表；必要时从旧配置迁移。"""
        with self._lock:
            data = self._read_file()
            items = data.get("items")
            if isinstance(items, list):
                normalized_items = self._normalize_items(items)
                if normalized_items != items:
                    self._write_file({"items": normalized_items})
                return [self._copy_item(item) for item in normalized_items]

            legacy_items = config.get("trackers.items", default=[])
            if isinstance(legacy_items, list) and legacy_items:
                logger.info(f"检测到旧版 Tracker 配置，开始迁移到独立文件：{self._path}")
                copied_items = self._normalize_items(legacy_items)
                self._write_file({"items": copied_items})
                config.set("trackers.items", [])
                config.save()
                logger.info(f"Tracker 已迁移到独立文件：{self._path}")
                return [self._copy_item(item) for item in copied_items]

            if not self._path.exists():
                self._write_file(DEFAULT_TRACKERS_DATA)
            return []

    def save_items(self, items: list[dict]):
        """保存 tracker 列表到独立文件。"""
        payload = {"items": [self._copy_item(item) for item in items if isinstance(item, dict)]}
        with self._lock:
            self._write_file(payload)

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
        normalized_items = self._normalize_items(data.get("items", []))
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with file_lock(TRACKERS_LOCK_FILE):
            with self._path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(
                    {"items": normalized_items},
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                )

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



