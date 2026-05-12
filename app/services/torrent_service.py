"""
下载器连接池（qBittorrent / Transmission）
"""
import re
from typing import Optional
import qbittorrentapi
import transmission_rpc

from app.utils.logger import get_logger

logger = get_logger(__name__)


def _parse_host(host: str) -> tuple[str, str, int]:
    """
    解析 host 字段，提取协议、主机名和端口。
    host 格式支持：
    - https://qbittorrent.example.com:8080
    - http://qbittorrent.example.com
    - qbittorrent.example.com (默认 http:8080)

    Returns:
        (protocol, host_without_protocol, port)
    """
    host = host.strip()
    protocol = "http"
    port = 8080  # 默认端口

    # 提取协议
    if host.startswith("https://"):
        protocol = "https"
        host = host[8:]
    elif host.startswith("http://"):
        protocol = "http"
        host = host[7:]

    # 提取端口（如果指定）
    if ":" in host:
        parts = host.rsplit(":", 1)
        host = parts[0]
        try:
            port = int(parts[1])
        except ValueError:
            port = 8080

    return protocol, host, port


class TorrentClientBase:
    """下载器基类"""

    def __init__(self, host: str, port: int, username: str, password: str, apikey: str = ""):
        # 从 host 直接解析协议和完整 URL
        self._protocol, clean_host, parsed_port = _parse_host(host)
        # 如果 host 包含协议前缀，先去掉协议前缀再检查是否包含端口
        host_stripped = host.strip()
        if host_stripped.startswith("https://"):
            host_without_proto = host_stripped[8:]
        elif host_stripped.startswith("http://"):
            host_without_proto = host_stripped[7:]
        else:
            host_without_proto = host_stripped
        # 只有当去掉协议后仍然包含端口（:digits）时才使用解析出的端口
        has_port = bool(re.search(r':\d+$', host_without_proto))
        final_port = parsed_port if has_port else port
        self._host = clean_host
        self._port = final_port
        self._base_url = f"{self._protocol}://{clean_host}:{final_port}"
        self._username = username
        self._password = password
        self._apikey = (apikey or "").strip()
        self._use_ssl = self._protocol == "https"
        self._connected = False
        self._version: Optional[str] = None

    def ping(self) -> bool:
        """测试连接"""
        raise NotImplementedError

    def get_version(self) -> Optional[str]:
        """获取客户端版本"""
        raise NotImplementedError

    def get_trackers(self) -> list[str]:
        """获取当前下载器中的 Tracker URL 列表"""
        raise NotImplementedError

    @property
    def is_connected(self) -> bool:
        return self._connected


class QbittorrentClient(TorrentClientBase):
    """qBittorrent 客户端"""

    def __init__(self, host: str, port: int, username: str, password: str, apikey: str = ""):
        super().__init__(host, port, username, password, apikey)
        self._client: Optional[qbittorrentapi.Client] = None

    def _build_client(self) -> qbittorrentapi.Client:
        kwargs = {
            "host": self._base_url,
            "username": self._username,
            "password": self._password,
            "VERIFY_WEBUI_CERTIFICATE": False,
            "REQUESTS_ARGS": {"timeout": (10, 30)},
        }
        if self._apikey:
            kwargs["EXTRA_HEADERS"] = {"Authorization": f"Bearer {self._apikey}"}
        return qbittorrentapi.Client(**kwargs)

    def _login(self):
        """登录并初始化 qBittorrent API 客户端。"""
        try:
            client = self._build_client()
            if self._apikey:
                version = client.app_version()
            else:
                client.auth_log_in()
                version = client.app_version()

            self._client = client
            self._version = str(version).strip() or None
            self._connected = True
        except qbittorrentapi.LoginFailed as e:
            self._client = None
            self._connected = False
            logger.warning(f"qBittorrent 登录失败（{self._base_url}）：{e}")
        except qbittorrentapi.APIConnectionError as e:
            self._client = None
            self._connected = False
            logger.error(f"qBittorrent 连接失败（{self._base_url}）：{e}")
        except Exception as e:
            self._client = None
            self._connected = False
            logger.error(f"qBittorrent 初始化失败（{self._base_url}）：{e}")

    def _ensure_client(self) -> Optional[qbittorrentapi.Client]:
        if not self._client or not self._connected:
            self._login()
        return self._client if self._connected else None

    def ping(self) -> bool:
        try:
            self._login()
            if not self._connected:
                logger.warning(f"qBittorrent 连接失败（{self._base_url}）")
            return self._connected
        except Exception as e:
            logger.error(f"qBittorrent 连接失败（{self._base_url}）：{e}")
            return False

    def get_version(self) -> Optional[str]:
        """获取 qBittorrent 版本"""
        client = self._ensure_client()
        if not client:
            return None
        try:
            version = client.app_version()
            self._version = str(version).strip() or None
            return self._version
        except Exception as e:
            logger.warning(f"获取 qBittorrent 版本失败：{e}")
            return None

    def get_trackers(self) -> list[str]:
        """获取 qBittorrent 中所有种子的 Tracker URL 列表"""
        client = self._ensure_client()
        if not client:
            return []

        tracker_urls: set[str] = set()

        try:
            torrents = client.torrents_info()
            for torrent in torrents:
                torrent_hash = getattr(torrent, "hash", None)
                if not torrent_hash:
                    continue

                try:
                    trackers = client.torrents_trackers(torrent_hash=torrent_hash)
                except Exception as e:
                    logger.debug(f"获取 qBittorrent 种子 {torrent_hash} 的 Tracker 失败：{e}")
                    continue

                for tracker in trackers:
                    tracker_url = str(getattr(tracker, "url", "") or "").strip()
                    if tracker_url and "://" in tracker_url:
                        tracker_urls.add(tracker_url)
        except Exception as e:
            logger.warning(f"获取 qBittorrent Tracker 列表失败：{e}")
            return []

        return list(tracker_urls)


class TransmissionClient(TorrentClientBase):
    """Transmission 客户端"""

    def __init__(self, host: str, port: int, username: str, password: str, apikey: str = ""):
        super().__init__(host, port, username, password, apikey)
        self._client: Optional[transmission_rpc.Client] = None

    def _login(self):
        try:
            self._client = transmission_rpc.Client(
                protocol=self._protocol,
                host=self._host,
                port=self._port,
                username=self._username or None,
                password=self._password or None,
                timeout=30,
            )
            self._connected = True
        except Exception as e:
            self._client = None
            self._connected = False
            logger.error(f"Transmission 连接失败（{self._base_url}）：{e}")

    def _ensure_client(self) -> Optional[transmission_rpc.Client]:
        if not self._client or not self._connected:
            self._login()
        return self._client if self._connected else None

    def ping(self) -> bool:
        try:
            client = self._ensure_client()
            if not client:
                return False
            client.session_stats()
            self._connected = True
            return self._connected
        except Exception as e:
            logger.error(f"Transmission 连接失败（{self._base_url}）：{e}")
            return False

    def get_version(self) -> Optional[str]:
        """获取 Transmission 版本"""
        client = self._ensure_client()
        if not client:
            return None
        try:
            version = getattr(client, "server_version", None)
            if version:
                self._version = str(version)
                return self._version
            return None
        except Exception as e:
            logger.warning(f"获取 Transmission 版本失败：{e}")
            return None

    def get_trackers(self) -> list[str]:
        """获取 Transmission 中所有种子的 Tracker URL 列表"""
        client = self._ensure_client()
        if not client:
            return []

        tracker_urls: set[str] = set()
        try:
            torrents = client.get_torrents(arguments=["trackers"])
            for torrent in torrents:
                for tracker in getattr(torrent, "trackers", []) or []:
                    tracker_url = str(getattr(tracker, "announce", "") or "").strip()
                    if tracker_url and "://" in tracker_url:
                        tracker_urls.add(tracker_url)
        except Exception as e:
            logger.warning(f"获取 Transmission Tracker 列表失败：{e}")
            return []

        return list(tracker_urls)


def create_client(client_type: str, **kwargs) -> TorrentClientBase:
    """工厂方法：创建下载器客户端"""
    if client_type == "qbittorrent":
        return QbittorrentClient(**kwargs)
    elif client_type == "transmission":
        return TransmissionClient(**kwargs)
    else:
        raise ValueError(f"Unknown client type: {client_type}")
