"""
Tracker 业务逻辑

Tracker 存储在独立的 config/trackers.yaml 中，内部统一保存为带协议的站点根 URL。
所有变更通过 TrackerStore 保存，避免主配置文件持续膨胀。

用法：
    from app.services.tracker_service import tracker_service
    trackers = tracker_service.list_trackers()
    tracker = tracker_service.add_tracker(name="BTN", url="tracker.example.com")
    tracker_service.update_tracker(id, enabled=False)
    tracker_service.delete_tracker(id)
    tracker_service.batch_import(["tracker1.example.com", "https://tracker2.example.com/announce"])
"""
import hashlib
import re as re_module
from typing import Optional
from urllib.parse import urlparse

from app.services.cloudflare_detector import cloudflare_detector
from app.services.tracker_store import tracker_store
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 域名 / IPv4 正则（用于 Tracker 目标校验）
TRACKER_TARGET_RE = re_module.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*|\d{1,3}(?:\.\d{1,3}){3})$",
    re_module.IGNORECASE,
)


def _extract_host(value: str) -> str:
    """从输入中提取规范化后的主机名；支持完整 tracker URL 或裸域名。"""
    value = value.strip().lower()
    if not value:
        return ""

    if "://" in value:
        parsed = urlparse(value)
        host = (parsed.hostname or "").strip().lower()
    else:
        host = value.split("/", 1)[0].split(":", 1)[0].strip().lower()

    return host.rstrip(".")


def _normalize_target(value: str) -> str:
    """将输入统一规范为协议 + 主机名的目标；裸域名默认补 https://。"""
    value = value.strip().lower()
    if not value:
        return ""

    host = _extract_host(value)
    if not host:
        return ""

    scheme = "https"
    if "://" in value:
        parsed = urlparse(value)
        if parsed.scheme in {"http", "https", "udp"}:
            scheme = parsed.scheme

    return f"{scheme}://{host}"


def _gen_id(target: str) -> str:
    """根据规范化后的目标生成固定短 ID（8位十六进制）"""
    return hashlib.md5(target.strip().lower().encode()).hexdigest()[:8]


def _validate_target(value: str) -> bool:
    """验证 Tracker 目标格式（域名 / IPv4 / 完整 tracker URL）"""
    host = _extract_host(value)
    return bool(host and TRACKER_TARGET_RE.match(host))


class TrackerService:
    """Tracker 管理服务"""

    def __init__(self):
        pass

    def _get_items(self) -> list[dict]:
        """获取 tracker 列表（副本）"""
        return tracker_store.load_items()

    def _save_items(self, items: list[dict]):
        """保存 tracker 列表"""
        tracker_store.save_items(items)

    def _find_by_id(self, tracker_id: str) -> Optional[tuple[int, dict]]:
        """根据 ID 查找 tracker，返回 (index, item) 或 None"""
        items = self._get_items()
        for i, item in enumerate(items):
            if item.get("id") == tracker_id:
                return i, item
        return None

    def _find_by_url(self, url: str) -> Optional[tuple[int, dict]]:
        """根据规范化后的目标查找 tracker，返回 (index, item) 或 None"""
        items = self._get_items()
        normalized_target = _normalize_target(url)
        for i, item in enumerate(items):
            if _normalize_target(item.get("url", "")) == normalized_target:
                return i, item
        return None

    def _build_tracker_item(self, name: str, url: str, enabled: bool = True) -> dict:
        """构造单个 tracker 条目，但不立即保存。"""
        normalized_target = _normalize_target(url)
        normalized_host = _extract_host(url)
        if not _validate_target(url):
            raise ValueError(f"无效的 Tracker 地址: {url}")

        existing = self._find_by_url(normalized_target)
        if existing:
            raise ValueError(f"Tracker 已存在: {normalized_host}")

        detection = cloudflare_detector.detect(normalized_target)
        display_name = (name or "").strip() or normalized_host
        return {
            "id": _gen_id(normalized_target),
            "enabled": enabled,
            "name": display_name,
            "url": normalized_target,
            "ip": None,
            "is_cloudflare": detection["is_cloudflare"],
        }

    def list_trackers(self) -> list[dict]:
        """列出所有 tracker（副本）"""
        return self._get_items().copy()

    def list_enabled_cloudflare(self) -> list[dict]:
        """列出所有已启用且判定为 Cloudflare 的 tracker"""
        return [
            t for t in self._get_items()
            if t.get("enabled", True) and t.get("is_cloudflare", False)
        ]

    def get_tracker(self, tracker_id: str) -> Optional[dict]:
        """根据 ID 获取单个 tracker"""
        result = self._find_by_id(tracker_id)
        return result[1].copy() if result else None

    def add_tracker(
        self,
        name: str,
        url: str,
        enabled: bool = True,
    ) -> dict:
        """
        新增单个 tracker

        Returns:
            新增的 tracker dict（包含 id）

        Raises:
            ValueError: 目标格式无效或已存在
        """
        item = self._build_tracker_item(name=name, url=url, enabled=enabled)

        items = self._get_items()
        items.append(item)
        self._save_items(items)

        logger.info(f"Tracker 已添加：{item['name']}（{item['url']}），ID={item['id']}，Cloudflare={item['is_cloudflare']}")
        return item.copy()

    def update_tracker(
        self,
        tracker_id: str,
        name: Optional[str] = None,
        url: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> Optional[dict]:
        """
        更新 tracker（部分更新，只修改提供的字段）

        Returns:
            更新后的 tracker dict，不存在返回 None

        Raises:
            ValueError: 新地址格式无效或与其他 tracker 冲突
        """
        result = self._find_by_id(tracker_id)
        if not result:
            return None

        idx, item = result
        items = self._get_items()

        if name is not None:
            item["name"] = name.strip()

        if url is not None:
            normalized_target = _normalize_target(url)
            normalized_host = _extract_host(url)
            if not _validate_target(url):
                raise ValueError(f"无效的 Tracker 地址: {url}")
            conflict = self._find_by_url(normalized_target)
            if conflict and conflict[0] != idx:
                raise ValueError(f"域名已被其他 Tracker 使用: {normalized_host}")
            detection = cloudflare_detector.detect(normalized_target)
            item["url"] = normalized_target
            item["is_cloudflare"] = detection["is_cloudflare"]
            old_id = item["id"]

            new_id = _gen_id(normalized_target)
            if old_id != new_id:
                logger.warning(f"Tracker 地址已变更，ID 从 {old_id} 更新为 {new_id}")
                item["id"] = new_id

        if enabled is not None:
            item["enabled"] = enabled

        items[idx] = item
        self._save_items(items)

        logger.info(f"Tracker 已更新：ID={tracker_id}，名称={item['name']}，Cloudflare={item.get('is_cloudflare', False)}")
        return item.copy()

    def delete_tracker(self, tracker_id: str) -> bool:
        """
        删除 tracker

        Returns:
            True 删除成功，False tracker 不存在
        """
        result = self._find_by_id(tracker_id)
        if not result:
            return False

        idx, item = result
        items = self._get_items()
        items.pop(idx)
        self._save_items(items)

        logger.info(f"Tracker 已删除：ID={tracker_id}，名称={item['name']}")
        return True

    def clear_all_trackers(self) -> int:
        """
        清空全部 tracker

        Returns:
            被清空的 tracker 数量
        """
        items = self._get_items()
        cleared_count = len(items)
        if cleared_count == 0:
            return 0

        self._save_items([])
        logger.info(f"Tracker 已全部清空：数量={cleared_count}")
        return cleared_count

    def update_trackers_ip_by_urls(self, urls: list[str], ip: str) -> int:
        """按指定 tracker URL 集合批量更新当前 IP。"""
        ip = (ip or "").strip()
        if not ip:
            raise ValueError("IP 地址不能为空")
        if not re_module.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", ip):
            raise ValueError(f"无效的 IPv4 地址: {ip}")

        normalized_targets = {
            _normalize_target(url)
            for url in urls
            if _normalize_target(url)
        }
        if not normalized_targets:
            return 0

        items = self._get_items()
        if not items:
            return 0

        updated = 0
        for item in items:
            if _normalize_target(item.get("url", "")) not in normalized_targets:
                continue
            item["ip"] = ip
            updated += 1

        if updated:
            self._save_items(items)
            logger.info(f"Tracker 当前 IP 已按 URL 集合批量更新：数量={updated}，IP={ip}")
        return updated

    def batch_import(
        self,
        urls: list[str],
        enabled: bool = True,
    ) -> tuple[int, int, list[dict]]:
        """
        批量导入 tracker 站点 URL

        Args:
            urls: 域名或完整 tracker URL 列表（支持逗号/换行/空格分隔的字符串）
            enabled: 是否默认启用

        Returns:
            (imported_count, skipped_count, imported_items)
        """
        if isinstance(urls, str):
            urls = re_module.split(r"[\n,;]+", urls)
        urls = [u.strip() for u in urls if u.strip()]

        items = self._get_items()
        existing_targets = {
            _normalize_target(item.get("url", ""))
            for item in items
            if item.get("url")
        }

        imported_items: list[dict] = []
        skipped = 0

        for url in urls:
            try:
                normalized_target = _normalize_target(url)
                normalized_host = _extract_host(url)
                if not _validate_target(url) or not normalized_host or not normalized_target:
                    raise ValueError(f"无效的 Tracker 地址: {url}")
                if normalized_target in existing_targets:
                    raise ValueError(f"Tracker 已存在: {normalized_target}")

                detection = cloudflare_detector.detect(normalized_target)
                item = {
                    "id": _gen_id(normalized_target),
                    "enabled": enabled,
                    "name": self._name_from_url(normalized_target),
                    "url": normalized_target,
                    "ip": None,
                    "is_cloudflare": detection["is_cloudflare"],
                }

                items.append(item)
                imported_items.append(item)
                existing_targets.add(normalized_target)
            except ValueError:
                skipped += 1
                logger.debug(f"跳过 Tracker（重复或无效）：{url}")

        if imported_items:
            self._save_items(items)

        logger.debug(f"Tracker 批量入库结束：新增 {len(imported_items)}，跳过 {skipped}")
        return len(imported_items), skipped, [item.copy() for item in imported_items]

    @staticmethod
    def _name_from_url(url: str) -> str:
        """从输入中提取名称（统一取主机名部分）"""
        host = _extract_host(url)
        return host or url.strip().lower()


tracker_service = TrackerService()





