"""
下载器连接池（qBittorrent / Transmission）
"""
import base64
import re
from urllib.parse import urlparse
import httpx
from typing import Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)



def _parse_host(host: str) -> tuple[str, str, int]:
    """
    解析 host 字段，提取协议、主机名和端口。
    host 格式支持：
    - https://qbittorrent.example.com:8443
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

    def __init__(self, host: str, port: int, username: str, password: str):
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
        self._base_url = f"{self._protocol}://{clean_host}:{final_port}"
        self._username = username
        self._password = password
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

    def __init__(self, host: str, port: int, username: str, password: str):
        super().__init__(host, port, username, password)
        self._sid: Optional[str] = None

    def _login(self):
        """登录获取 Session ID"""
        with httpx.Client(base_url=self._base_url, timeout=10, verify=False) as client:
            resp = client.post("/api/v2/auth/login", data={
                "username": self._username,
                "password": self._password,
            })
            if resp.status_code == 200:
                self._sid = resp.cookies.get("SID")
                self._connected = bool(self._sid)
                if not self._connected:
                    logger.warning("qBittorrent 登录成功但未获取到会话标识")
            else:
                self._connected = False
                logger.warning(f"qBittorrent 登录失败，状态码：{resp.status_code}")

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
        if not self._sid:
            self._login()
        if not self._sid:
            return None
        try:
            with httpx.Client(base_url=self._base_url, timeout=10, verify=False, cookies={"SID": self._sid}) as client:
                resp = client.get("/api/v2/app/version")
                if resp.status_code == 200:
                    self._version = resp.text.strip()
                    return self._version
                return None
        except Exception as e:
            logger.warning(f"获取 qBittorrent 版本失败：{e}")
            return None

    def get_trackers(self) -> list[str]:
        """获取 qBittorrent 中所有种子的 Tracker URL 列表"""
        if not self._sid:
            self._login()
        if not self._sid:
            return []

        tracker_urls: set[str] = set()

        try:
            with httpx.Client(base_url=self._base_url, timeout=15, verify=False, cookies={"SID": self._sid}) as client:
                torrents_resp = client.get("/api/v2/torrents/info")
                if torrents_resp.status_code != 200:
                    logger.warning(f"获取 qBittorrent 种子列表失败，状态码：{torrents_resp.status_code}")
                    return []

                torrents = torrents_resp.json()
                for torrent in torrents:
                    torrent_hash = torrent.get("hash")
                    if not torrent_hash:
                        continue

                    trackers_resp = client.get("/api/v2/torrents/trackers", params={"hash": torrent_hash})
                    if trackers_resp.status_code != 200:
                        logger.debug(f"获取 qBittorrent 种子 {torrent_hash} 的 Tracker 失败，状态码：{trackers_resp.status_code}")
                        continue

                    for tracker in trackers_resp.json():
                        tracker_url = (tracker.get("url") or "").strip()
                        if tracker_url and "://" in tracker_url:
                            tracker_urls.add(tracker_url)
        except Exception as e:
            logger.warning(f"获取 qBittorrent Tracker 列表失败：{e}")
            return []

        return list(tracker_urls)



class TransmissionClient(TorrentClientBase):
    """Transmission 客户端"""

    def __init__(self, host: str, port: int, username: str, password: str):
        super().__init__(host, port, username, password)
        self._session_id: Optional[str] = None

    def _get_headers(self) -> dict:
        """获取认证 headers"""
        headers = {}
        if self._username:
            credentials = base64.b64encode(
                f"{self._username}:{self._password}".encode()
            ).decode()
            headers["Authorization"] = f"Basic {credentials}"
        if self._session_id:
            headers["X-Transmission-Session-Id"] = self._session_id
        return headers

    def _rpc(self, payload: dict) -> Optional[dict]:
        try:
            with httpx.Client(base_url=self._base_url, timeout=15, verify=False, headers=self._get_headers()) as client:
                resp = client.post("/transmission/rpc", json=payload)
                if resp.status_code == 409:
                    self._session_id = resp.headers.get("X-Transmission-Session-Id")
                    resp = client.post(
                        "/transmission/rpc",
                        json=payload,
                        headers=self._get_headers(),
                    )
                if resp.status_code != 200:
                    return None
                return resp.json()
        except Exception as e:
            logger.warning(f"Transmission RPC 请求失败：{e}")
            return None

    def ping(self) -> bool:
        try:
            data = self._rpc({"method": "session-stats"})
            self._connected = bool(data)
            return self._connected
        except Exception as e:
            logger.error(f"Transmission 连接失败（{self._base_url}）：{e}")
            return False

    def get_version(self) -> Optional[str]:
        """获取 Transmission 版本"""
        data = self._rpc({"method": "session-get"})
        if not data:
            return None
        try:
            version = data.get("arguments", {}).get("version")
            if version:
                self._version = version
                return self._version
            return None
        except Exception as e:
            logger.warning(f"获取 Transmission 版本失败：{e}")
            return None

    def get_trackers(self) -> list[str]:
        """获取 Transmission 中所有种子的 Tracker URL 列表"""
        data = self._rpc({"method": "torrent-get", "arguments": {"fields": ["trackers"]}})
        if not data or data.get("result") != "success":
            return []

        tracker_urls: set[str] = set()
        torrents = data.get("arguments", {}).get("torrents", [])
        for torrent in torrents:
            for tracker in torrent.get("trackers", []):
                tracker_url = (tracker.get("announce") or "").strip()
                if tracker_url and "://" in tracker_url:
                    tracker_urls.add(tracker_url)

        return list(tracker_urls)



def create_client(client_type: str, **kwargs) -> TorrentClientBase:
    """工厂方法：创建下载器客户端"""
    if client_type == "qbittorrent":
        return QbittorrentClient(**kwargs)
    elif client_type == "transmission":
        return TransmissionClient(**kwargs)
    else:
        raise ValueError(f"Unknown client type: {client_type}")
