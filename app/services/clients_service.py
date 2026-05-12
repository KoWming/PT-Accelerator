"""
下载器客户端服务

下载器配置存储在 config.downloaders.items。
"""
import hashlib
import re as re_module
from typing import Optional
from urllib.parse import urlparse

from app.utils.logger import get_logger


logger = get_logger(__name__)

# 支持的客户端类型
SUPPORTED_TYPES = ["qbittorrent", "transmission"]

# 默认端口
DEFAULT_PORTS = {
    "qbittorrent": 8080,
    "transmission": 9091,
}

# 类型展示信息
CLIENT_TYPE_OPTIONS = [
    {
        "type": "qbittorrent",
        "name": "qBittorrent",
        "default_port": DEFAULT_PORTS["qbittorrent"],
        "fields": ["host", "port", "username", "password", "apikey"],
    },
    {
        "type": "transmission",
        "name": "Transmission",
        "default_port": DEFAULT_PORTS["transmission"],
        "fields": ["host", "port", "username", "password"],
    },
]

# 主机名/域名正则
HOST_RE = re_module.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*|\d{1,3}(?:\.\d{1,3}){3})$",
    re_module.IGNORECASE,
)


def _validate_type(client_type: str) -> bool:
    """验证下载器客户端类型。"""
    return client_type in SUPPORTED_TYPES


def _validate_host(host: str) -> bool:
    """验证主机格式（支持 http:// 或 https:// 前缀）"""
    host = host.strip()
    if host.startswith("https://"):
        host = host[8:]
    elif host.startswith("http://"):
        host = host[7:]
    return bool(HOST_RE.match(host))


def _parse_host(host: str) -> tuple[str, str, int]:
    """
    解析 host 字段，提取协议、主机名和端口。

    Returns:
        (protocol, host_without_port, port)
    """
    host = host.strip()
    protocol = "http"
    port = 8080

    if host.startswith("https://"):
        protocol = "https"
        host = host[8:]
    elif host.startswith("http://"):
        host = host[7:]

    if ":" in host:
        parts = host.rsplit(":", 1)
        host = parts[0]
        try:
            port = int(parts[1])
        except ValueError:
            port = 8080

    return protocol, host, port


def _normalize_host_and_port(host: str, port: int) -> tuple[str, int, str]:
    """规范化 host 和 port，返回 (host_for_save, port_for_save, host_clean)。"""
    host = host.strip()
    protocol, host_clean, parsed_port = _parse_host(host)

    has_explicit_port = bool(re_module.search(r':\d+$', host))
    final_port = parsed_port if has_explicit_port else port

    if not _validate_host(host_clean):
        raise ValueError(f"无效的主机格式: {host_clean}")

    if not (1 <= final_port <= 65535):
        raise ValueError(f"无效的端口范围: {final_port}，端口必须在 1-65535 之间")

    if host.startswith(("http://", "https://")):
        host_for_save = host
    else:
        host_for_save = f"{protocol}://{host_clean}"

    return host_for_save, final_port, host_clean


def _gen_id(client_type: str, host: str, port: int) -> str:
    """根据 type+host+port 生成客户端ID"""
    key = f"{client_type}:{host.strip().lower()}:{port}"
    return hashlib.md5(key.encode()).hexdigest()[:8]


def _build_client_item(
    *,
    client_id: str,
    enabled: bool,
    name: str,
    client_type: str,
    host: str,
    port: int,
    username: str = "",
    password: str = "",
    apikey: str = "",
    version: Optional[str] = None,
) -> dict:
    """统一构造下载器配置项，固定字段顺序。"""
    item = {
        "id": client_id,
        "enabled": enabled,
        "name": name.strip(),
        "type": client_type,
        "host": host,
        "port": port,
        "username": username,
        "password": password,
    }
    if apikey:
        item["apikey"] = apikey
    if version:
        item["version"] = version
    return item


def _normalize_tracker_target(value: str) -> str:
    """提取下载器中的 Tracker 目标，保留协议与端口，仅保留到主机名层级。"""
    raw = (value or "").strip().lower()
    if not raw or "://" not in raw:
        return ""

    parsed = urlparse(raw)
    host = (parsed.hostname or "").strip().lower().rstrip(".")
    scheme = (parsed.scheme or "").strip().lower()
    if not host or scheme not in {"http", "https", "udp"}:
        return ""

    if ":" in host and not host.startswith("["):
        host = f"[{host}]"

    if parsed.port:
        return f"{scheme}://{host}:{parsed.port}"
    return f"{scheme}://{host}"


class ClientsService:
    """下载器客户端管理服务"""

    def __init__(self):
        pass

    def _get_items(self) -> list[dict]:
        """获取 downloaders.items 列表"""
        from app.config import config
        return config.get("downloaders.items", default=[])

    def _save_items(self, items: list[dict]):
        """保存 downloaders.items 列表"""
        from app.config import config
        config.set("downloaders.items", items)
        config.save()

    def _find_by_id(self, client_id: str) -> Optional[tuple[int, dict]]:
        """根据ID查找客户端，返回 (index, item) 或 None"""
        items = self._get_items()
        for i, item in enumerate(items):
            if item.get("id") == client_id:
                return i, item
        return None

    def _find_by_key(self, client_type: str, host: str, port: int) -> Optional[tuple[int, dict]]:
        """根据 type+host+port 查找客户端"""
        items = self._get_items()
        key = f"{client_type}:{host.strip().lower()}:{port}"
        for i, item in enumerate(items):
            item_key = f"{item.get('type')}:{item.get('host', '').strip().lower()}:{item.get('port')}"
            if item_key == key:
                return i, item
        return None

    def list_clients(self) -> list[dict]:
        """列出所有下载器客户端"""
        return self._get_items().copy()

    def get_supported_types(self) -> list[dict]:
        """获取支持的客户端类型列表。"""
        return [item.copy() for item in CLIENT_TYPE_OPTIONS]

    def list_enabled(self) -> list[dict]:
        """列出所有已启用的下载器客户端"""
        return [c for c in self._get_items() if c.get("enabled", True)]

    def get_client(self, client_id: str) -> Optional[dict]:
        """根据ID获取单个客户端"""
        result = self._find_by_id(client_id)
        return result[1].copy() if result else None

    def add_client(
        self,
        name: str,
        client_type: str,
        host: str,
        port: int,
        username: str = "",
        password: str = "",
        apikey: str = "",
        enabled: bool = True,
        version: Optional[str] = None,
    ) -> dict:
        """添加新的下载器客户端。"""
        if not _validate_type(client_type):
            raise ValueError(f"不支持的客户端类型: {client_type}，支持的类型: {', '.join(SUPPORTED_TYPES)}")

        host_for_save, port_for_save, host_clean = _normalize_host_and_port(host, port)

        existing = self._find_by_key(client_type, host_clean, port_for_save)
        if existing:
            idx, item = existing
            items = self._get_items()
            updated_item = _build_client_item(
                client_id=item["id"],
                enabled=enabled,
                name=name,
                client_type=client_type,
                host=host_for_save,
                port=port_for_save,
                username=username,
                password=password,
                apikey=apikey or item.get("apikey", ""),
                version=version or item.get("version"),
            )
            items[idx] = updated_item
            self._save_items(items)
            logger.info(f"已更新现有下载器客户端：{name}（{client_type}@{host_clean}:{port_for_save}），ID={item['id']}")
            return updated_item.copy()

        client_id = _gen_id(client_type, host_clean, port_for_save)
        item = _build_client_item(
            client_id=client_id,
            enabled=enabled,
            name=name,
            client_type=client_type,
            host=host_for_save,
            port=port_for_save,
            username=username,
            password=password,
            apikey=apikey,
            version=version,
        )

        items = self._get_items()
        items.append(item)
        self._save_items(items)

        logger.info(f"已添加下载器客户端：{name}（{client_type}@{host_clean}:{port_for_save}），ID={client_id}")
        return item.copy()

    def update_client(
        self,
        client_id: str,
        name: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        apikey: Optional[str] = None,
        enabled: Optional[bool] = None,
        version: Optional[str] = None,
    ) -> Optional[dict]:
        """更新客户端（部分更新）。"""
        result = self._find_by_id(client_id)
        if not result:
            return None

        idx, item = result
        items = self._get_items()

        next_name = name.strip() if name is not None else str(item.get("name") or "").strip()
        next_host = item.get("host", "")
        next_port = item.get("port")

        if host is not None or port is not None:
            input_host = host if host is not None else item.get("host", "")
            input_port = port if port is not None else item.get("port")
            next_host, next_port, _ = _normalize_host_and_port(input_host, input_port)

        next_username = username if username is not None else item.get("username", "")
        next_password = password if password is not None else item.get("password", "")
        next_apikey = apikey if apikey is not None else item.get("apikey", "")
        next_enabled = enabled if enabled is not None else item.get("enabled", True)
        next_version = version if version is not None else item.get("version")

        updated_item = _build_client_item(
            client_id=client_id,
            enabled=bool(next_enabled),
            name=next_name,
            client_type=item.get("type", ""),
            host=next_host,
            port=next_port,
            username=str(next_username),
            password=str(next_password),
            apikey=str(next_apikey),
            version=str(next_version) if next_version else None,
        )

        items[idx] = updated_item
        self._save_items(items)

        logger.info(f"下载器客户端已更新：ID={client_id}，名称={updated_item['name']}")
        return updated_item.copy()

    def delete_client(self, client_id: str) -> bool:
        """根据ID删除客户端。"""
        result = self._find_by_id(client_id)
        if not result:
            return False

        idx, item = result
        items = self._get_items()
        items.pop(idx)
        self._save_items(items)

        logger.info(f"下载器客户端已删除：ID={client_id}，名称={item['name']}")
        return True

    def test_connection(self, client_id: str) -> dict:
        """测试客户端连接，并保存版本信息。"""
        from app.services.torrent_service import create_client

        result = self._find_by_id(client_id)
        if not result:
            return {"success": False, "message": f"客户端不存在: {client_id}", "version": None}

        idx, item = result

        try:
            client = create_client(
                client_type=item["type"],
                host=item["host"],
                port=item["port"],
                username=item.get("username", ""),
                password=item.get("password", ""),
                apikey=item.get("apikey", ""),
            )
            connected = client.ping()
            if connected:
                version = client.get_version()
                items = self._get_items()
                items[idx] = _build_client_item(
                    client_id=item["id"],
                    enabled=item.get("enabled", True),
                    name=item.get("name", ""),
                    client_type=item["type"],
                    host=item["host"],
                    port=item["port"],
                    username=item.get("username", ""),
                    password=item.get("password", ""),
                    apikey=item.get("apikey", ""),
                    version=version,
                )
                self._save_items(items)
                logger.info(f"下载器连接成功: {item['name']}, 版本: {version}")
                return {"success": True, "message": "连接成功", "version": version}
            return {"success": False, "message": "连接失败", "version": None}
        except Exception as e:
            logger.error(f"下载器连接测试失败: {client_id} - {e}")
            return {"success": False, "message": f"连接异常: {str(e)}", "version": None}

    def test_connection_by_config(
        self,
        client_type: str,
        host: str,
        port: int,
        username: str = "",
        password: str = "",
        apikey: str = "",
    ) -> dict:
        """使用提供的配置测试连接（不保存）。"""
        from app.services.torrent_service import create_client

        try:
            client = create_client(
                client_type=client_type,
                host=host,
                port=port,
                username=username,
                password=password,
                apikey=apikey,
            )
            connected = client.ping()
            if connected:
                version = client.get_version()
                logger.info(f"下载器连接成功: {client_type}@{host}:{port}, 版本: {version}")
                return {"success": True, "message": "连接成功", "version": version}
            return {"success": False, "message": "连接失败", "version": None}
        except Exception as e:
            logger.error(f"下载器连接测试失败: {e}")
            return {"success": False, "message": f"连接异常: {str(e)}", "version": None}

    def import_trackers_from_clients(self) -> dict:
        """从所有已启用下载器导入 Tracker：保留协议去重、Cloudflare 先筛后存。"""
        from app.services.cloudflare_detector import cloudflare_detector
        from app.services.torrent_service import create_client
        from app.services.tracker_service import tracker_service

        enabled_clients = self.list_enabled()
        if not enabled_clients:
            return {
                "imported": 0,
                "skipped": 0,
                "message": "当前没有已启用的下载器，无法导入 Tracker",
                "client_summary": "未找到已启用的下载器",
                "cloudflare_domains": [],
                "non_cloudflare_domains": [],
                "torrent_count": 0,
                "tracker_count": 0,
                "unique_tracker_count": 0,
            }

        logger.info(f"开始从下载器导入 Tracker：已启用下载器 {len(enabled_clients)} 个")

        tracker_targets: set[str] = set()
        client_messages: list[str] = []
        torrent_count = 0
        tracker_count = 0

        for item in enabled_clients:
            name = item.get("name") or item.get("id") or "未命名下载器"
            try:
                logger.info(f"开始读取下载器 Tracker：{name}（{item['type']}）")
                client = create_client(
                    client_type=item["type"],
                    host=item["host"],
                    port=item["port"],
                    username=item.get("username", ""),
                    password=item.get("password", ""),
                )
                urls = client.get_trackers()
                normalized_targets = {
                    normalized
                    for url in urls
                    if (normalized := _normalize_tracker_target(url))
                }
                tracker_targets.update(normalized_targets)
                tracker_count += len(urls)
                torrent_count += len(normalized_targets)
                logger.info(
                    f"下载器 Tracker 读取完成：{name}，原始 {len(urls)} 条，规范化后唯一目标 {len(normalized_targets)} 条"
                )
                client_messages.append(f"{name}: {len(normalized_targets)} 个唯一 Tracker 目标")
            except Exception as e:
                logger.warning(f"从下载器导入 Tracker 失败：{name} - {e}")
                client_messages.append(f"{name}: 失败({str(e)})")

        unique_targets = sorted(tracker_targets)
        if not unique_targets:
            logger.info("下载器 Tracker 读取结束，但未发现可导入的唯一目标")
            return {
                "imported": 0,
                "skipped": 0,
                "message": "未从已启用下载器中发现可导入的 Tracker 目标",
                "client_summary": "；".join(client_messages),
                "cloudflare_domains": [],
                "non_cloudflare_domains": [],
                "torrent_count": torrent_count,
                "tracker_count": tracker_count,
                "unique_tracker_count": 0,
            }

        logger.info(
            f"下载器 Tracker 汇总完成：原始 {tracker_count} 条，汇总后唯一目标 {len(unique_targets)} 条，开始做 Cloudflare 筛选"
        )

        cloudflare_targets: list[str] = []
        non_cloudflare_targets: list[str] = []
        for target in unique_targets:
            detection = cloudflare_detector.detect(target)
            if detection.get("is_cloudflare"):
                logger.info(f"Cloudflare 命中：{target}，来源={detection.get('source')}")
                cloudflare_targets.append(target)
            else:
                logger.info(f"Cloudflare 未命中：{target}，来源={detection.get('source')}")
                non_cloudflare_targets.append(target)

        logger.info(
            f"Cloudflare 筛选完成：命中 {len(cloudflare_targets)} 条，未命中 {len(non_cloudflare_targets)} 条，开始批量导入 Tracker"
        )

        imported = 0
        skipped = 0
        if cloudflare_targets:
            imported, skipped, _ = tracker_service.batch_import(cloudflare_targets, enabled=True)
        else:
            logger.info("本轮没有命中的 Cloudflare Tracker，跳过批量导入")

        logger.info(
            f"从下载器导入 Tracker 完成：唯一目标 {len(unique_targets)}，"
            f"Cloudflare站点 {len(cloudflare_targets)}，非Cloudflare站点 {len(non_cloudflare_targets)}，"
            f"新增 {imported}，跳过 {skipped}"
        )

        return {
            "imported": imported,
            "skipped": skipped,
            "message": f"导入完成：检测到 {len(unique_targets)} 个唯一 Tracker 目标，筛出 {len(cloudflare_targets)} 个 Cloudflare 站点，新增 {imported} 个，跳过 {skipped} 个",
            "client_summary": "；".join(client_messages),
            "cloudflare_domains": cloudflare_targets,
            "non_cloudflare_domains": non_cloudflare_targets,
            "torrent_count": torrent_count,
            "tracker_count": tracker_count,
            "unique_tracker_count": len(unique_targets),
        }


clients_service = ClientsService()
