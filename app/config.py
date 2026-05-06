"""
配置唯一入口（加载 / 写入 / 迁移）

所有模块通过以下方式访问配置：
    from app.config import config
    value = config.get("cfst.threads", default=200)

禁止直接读 YAML 文件，所有配置读写必须通过 ConfigManager。
"""
import hashlib
import os
import platform
import yaml
from pathlib import Path
from typing import Any, Optional, Callable
from threading import Lock

from app.utils.logger import get_logger
from app.utils.file_lock import file_lock

logger = get_logger(__name__)

# ==================== 路径配置 ====================
CONFIG_DIR = os.environ.get("CONFIG_DIR", "config")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.yaml")
SCHEMA_VERSION_PATH = os.path.join(CONFIG_DIR, ".schema_version")
LOCK_FILE = CONFIG_PATH + ".lock"

# 当前 schema 版本
CURRENT_SCHEMA_VERSION = 1

WINDOWS_HOSTS_PATH = "C:\\Windows\\System32\\drivers\\etc\\hosts"
LINUX_HOSTS_PATH = "/etc/hosts"


def _default_hosts_target_path() -> str:
    """根据当前运行环境返回默认 hosts 路径。"""
    return WINDOWS_HOSTS_PATH if platform.system().lower() == "windows" else LINUX_HOSTS_PATH


def _normalize_hosts_target_path(raw_path: Any) -> str:
    """规范化 hosts 路径，并在 Linux 环境兼容历史 Windows 默认值。"""
    path = str(raw_path or "").strip()
    default_path = _default_hosts_target_path()

    if not path:
        return default_path

    if platform.system().lower() != "windows" and path == WINDOWS_HOSTS_PATH:
        return LINUX_HOSTS_PATH

    return path


def _gen_downloader_id(client_type: str, host: str, port: int) -> str:
    """根据 type+host+port 生成稳定的下载器 ID。"""
    key = f"{client_type}:{host.strip().lower()}:{port}"
    return hashlib.md5(key.encode()).hexdigest()[:8]


def _build_downloader_item(
    *,
    client_id: str,
    enabled: bool,
    name: str,
    client_type: str,
    host: str,
    port: int,
    username: str = "",
    password: str = "",
    version: str = "",
) -> dict:
    """统一构造下载器配置项，固定字段顺序。"""
    item = {
        "id": client_id,
        "enabled": enabled,
        "name": name,
        "type": client_type,
        "host": host,
        "port": port,
        "username": username,
        "password": password,
    }
    if version:
        item["version"] = version
    return item


DEFAULT_DOWNLOADER_ITEMS = [
    _build_downloader_item(
        client_id=_gen_downloader_id("qbittorrent", "localhost", 8080),
        enabled=False,
        name="qBittorrent",
        client_type="qbittorrent",
        host="http://localhost",
        port=8080,
    ),
    _build_downloader_item(
        client_id=_gen_downloader_id("transmission", "localhost", 9091),
        enabled=False,
        name="Transmission",
        client_type="transmission",
        host="http://localhost",
        port=9091,
    ),
]


def _normalize_downloader_item(item: dict) -> dict:
    """清理旧下载器配置字段，并统一字段顺序。"""
    client_type = str(item.get("type") or "qbittorrent").strip() or "qbittorrent"
    host = str(item.get("host") or "http://localhost").strip() or "http://localhost"

    raw_port = item.get("port", 8080)
    try:
        port = int(raw_port)
    except (TypeError, ValueError):
        port = 8080

    client_id = str(item.get("id") or _gen_downloader_id(client_type, host, port)).strip()
    if not client_id:
        client_id = _gen_downloader_id(client_type, host, port)

    return _build_downloader_item(
        client_id=client_id,
        enabled=bool(item.get("enabled", True)),
        name=str(item.get("name") or "").strip(),
        client_type=client_type,
        host=host,
        port=port,
        username=str(item.get("username") or ""),
        password=str(item.get("password") or ""),
        version=str(item.get("version") or ""),
    )


def _normalize_downloaders_config(data: dict) -> dict:
    """统一 downloaders.items 配置结构。"""
    normalized = ConfigManager._deep_copy(data)
    normalized.pop("trackers", None)
    downloaders = normalized.setdefault("downloaders", {})
    items = downloaders.get("items")

    if not isinstance(items, list):
        downloaders["items"] = ConfigManager._deep_copy(DEFAULT_DOWNLOADER_ITEMS)
        return normalized

    downloaders["items"] = [
        _normalize_downloader_item(item)
        for item in items
        if isinstance(item, dict)
    ]
    return normalized

def _normalize_backup_config(data: dict) -> dict:
    """统一 backup 配置结构，并移除废弃历史字段。"""
    normalized = ConfigManager._deep_copy(data)
    backup = normalized.setdefault("backup", {})
    existing_password = str(backup.get("webdav_password") or "")

    normalized["backup"] = {
        "webdav_enabled": bool(backup.get("webdav_enabled", False)),
        "webdav_url": str(backup.get("webdav_url") or "").strip().rstrip("/"),
        "webdav_username": str(backup.get("webdav_username") or ""),
        "webdav_password": existing_password,
        "webdav_path": str(backup.get("webdav_path") or "/backups").strip() or "/backups",
        "local_keep_count": max(1, min(30, int(backup.get("local_keep_count", 7) or 7))),
    }
    return normalized

DEFAULT_HOSTS_SOURCES = [
    {
        "id": hashlib.md5("https://gitlab.com/ineo6/hosts/-/raw/master/next-hosts".encode()).hexdigest()[:8],
        "enabled": True,
        "name": "GitHub源（ineo6）",
        "url": "https://gitlab.com/ineo6/hosts/-/raw/master/next-hosts",
    },
    {
        "id": hashlib.md5("https://ghfast.top/https://raw.githubusercontent.com/kekylin/hosts/main/hosts".encode()).hexdigest()[:8],
        "enabled": True,
        "name": "GitHub源（kekylin）",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/kekylin/hosts/main/hosts",
    },
    {
        "id": hashlib.md5("https://ghfast.top/https://raw.githubusercontent.com/wjz304/hosts/main/hosts".encode()).hexdigest()[:8],
        "enabled": True,
        "name": "GitHub源（wjz304）",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/wjz304/hosts/main/hosts",
    },
    {
        "id": hashlib.md5("https://ghfast.top/https://raw.githubusercontent.com/ChenXinBest/hosts_check/refs/heads/master/hosts.txt".encode()).hexdigest()[:8],
        "enabled": True,
        "name": "GitHub源（混合）",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/ChenXinBest/hosts_check/refs/heads/master/hosts.txt",
    },
    {
        "id": hashlib.md5("https://ghfast.top/https://raw.githubusercontent.com/cnwikee/CheckTMDB/refs/heads/main/Tmdb_host_ipv4".encode()).hexdigest()[:8],
        "enabled": True,
        "name": "GitHub源（TMDB）",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/cnwikee/CheckTMDB/refs/heads/main/Tmdb_host_ipv4",
    },
    {
        "id": hashlib.md5("https://ghfast.top/https://raw.githubusercontent.com/521xueweihan/GitHub520/refs/heads/main/hosts".encode()).hexdigest()[:8],
        "enabled": True,
        "name": "GitHub源（521xueweihan）",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/521xueweihan/GitHub520/refs/heads/main/hosts",
    },
]


def _normalize_hosts_source_item(item: dict) -> dict:
    url = str(item.get("url") or "").strip()
    source_id = str(item.get("id") or hashlib.md5(url.encode()).hexdigest()[:8]).strip()
    if not source_id:
        source_id = hashlib.md5(url.encode()).hexdigest()[:8]

    return {
        "id": source_id,
        "enabled": bool(item.get("enabled", True)),
        "name": str(item.get("name") or "").strip(),
        "url": url,
    }


def _normalize_hosts_config(data: dict) -> dict:
    """统一 hosts 配置结构，移除历史字段并补齐默认源。"""
    normalized = ConfigManager._deep_copy(data)
    hosts = normalized.setdefault("hosts", {})
    raw_sources = hosts.get("sources")

    if not isinstance(raw_sources, list) or not raw_sources:
        sources = ConfigManager._deep_copy(DEFAULT_HOSTS_SOURCES)
    else:
        sources = [
            _normalize_hosts_source_item(item)
            for item in raw_sources
            if isinstance(item, dict) and str(item.get("url") or "").strip()
        ]
        if not sources:
            sources = ConfigManager._deep_copy(DEFAULT_HOSTS_SOURCES)

    normalized["hosts"] = {
        "sources": sources,
        "backup_enabled": bool(hosts.get("backup_enabled", True)),
        "target_path": _normalize_hosts_target_path(hosts.get("target_path")),
    }
    return normalized


# ==================== 默认配置 ====================
DEFAULT_CONFIG: dict = {

    "schema_version": CURRENT_SCHEMA_VERSION,


    "app": {
        "version": "3.0.0",
        "debug": False,
    },
    "auth": {
        "username": "admin",
        "password_hash": "",
    },
    "cfst": {
        "threads": 200,
        "ping_times": 4,
        "download_count": 20,

        "download_time": 10,
        "timeout_seconds": 300,
        "tcp_port": 443,
        "url": "",
        "httping": False,
        "httping_code": "",
        "cfcolo": "",
        "min_delay": 0,
        "max_delay": 200,
        "max_loss_rate": 1.0,
        "min_speed": 0.0,
        "show_count": 10,
        "test_all": False,
        "disable_download": False,
        "debug": False,
        "additional_args": "",
        "binary_auto_install": True,
        "binary_path": "",
    },
    "hosts": {
        "sources": DEFAULT_HOSTS_SOURCES,
        "backup_enabled": True,
        "target_path": _default_hosts_target_path(),
    },

    "cloudflare_domains": [],

    "downloaders": {
        "items": DEFAULT_DOWNLOADER_ITEMS,
    },

    "scheduler": {
        "jobs": {
            "cfst": {
                "name": "CFST 测速任务",
                "trigger": "cron",
                "enabled": True,
                "interval_seconds": 3600,
                "cron_expr": "0 0 * * *",
            },
        },
    },
    "backup": {
        "webdav_enabled": False,
        "webdav_url": "",
        "webdav_username": "",
        "webdav_password": "",
        "webdav_path": "/backups",
        "local_keep_count": 7,
    },
    "notify": {
        "channels": [],
        "events": {
            "cfst_completed": True,
            "hosts_updated": True,
            "backup_completed": True,
            "scheduler_error": True,
        },
    },
    "ikuai": {
        "enabled": False,
        "host": "",
        "port": 80,
        "username": "",
        "password": "",
    },
    "mihosts": {
        "enabled": False,
        "token": "",
        "app_id": "2882303761517675329",
        "device_id": "",
        "client_id": "2882303761517675329",
        "scope": "1+1000+3",
        "ignore": "",
    },
}



# ==================== 配置迁移 ====================
class ConfigMigration:
    """配置 schema 迁移器"""

    # 迁移函数字典：{from_version: function_to_upgrade_to_next}
    MIGRATIONS: dict[int, Callable[[dict], dict]] = {
        # 示例：
        # 1: lambda cfg: {...},  # v1 -> v2
        # 2: lambda cfg: {...},  # v2 -> v3
    }

    @classmethod
    def migrate(cls, data: dict) -> dict:
        """执行所有需要的迁移"""
        current_version = data.get("schema_version", 1)
        target_version = CURRENT_SCHEMA_VERSION

        if current_version == target_version:
            logger.debug(f"配置 schema 版本已是 v{target_version}")
            return data

        logger.info(f"正在迁移配置：v{current_version} -> v{target_version}")

        while current_version < target_version:
            migration_fn = cls.MIGRATIONS.get(current_version)
            if migration_fn is None:
                logger.warning(f"未找到 v{current_version} -> v{current_version + 1} 的迁移脚本，跳过")
                current_version += 1
                continue

            data = migration_fn(data)
            data["schema_version"] = current_version + 1
            current_version += 1
            logger.info(f"配置已迁移到 v{current_version}")

        return data


# ==================== 配置管理器 ====================
class ConfigManager:
    """
    线程安全的配置文件读写

    - 加载时自动合并默认配置
    - 保存时带文件锁保护
    - 自动执行 schema 迁移
    """

    def __init__(self, path: str = CONFIG_PATH):
        self._path = path
        self._lock = Lock()
        self._data: dict = {}
        self._loaded = False

    def load(self) -> dict:
        """
        加载配置（线程安全）
        1. 读取 YAML 文件
        2. 合并默认配置
        3. 执行迁移
        4. 返回合并后的配置
        """
        with self._lock:
            if os.path.exists(self._path):
                try:
                    with open(self._path, "r", encoding="utf-8") as f:
                        loaded = yaml.safe_load(f) or {}
                    logger.info(f"配置已加载：{self._path}")
                except yaml.YAMLError as e:
                    logger.error(f"解析配置 YAML 失败：{e}，使用默认配置")
                    loaded = {}
            else:
                logger.info(f"配置文件不存在：{self._path}，使用默认配置")
                loaded = {}

            # 合并默认配置（loaded 优先级更高）
            self._data = self._merge_defaults(loaded)

            # 执行迁移
            self._data = ConfigMigration.migrate(self._data)

            # 统一 downloaders.items 结构
            self._data = _normalize_downloaders_config(self._data)

            # 统一 backup 配置结构
            self._data = _normalize_backup_config(self._data)

            # 统一 hosts 配置结构
            self._data = _normalize_hosts_config(self._data)

            self._loaded = True

            return self._data.copy()



    def save(self, data: Optional[dict] = None):
        """
        保存配置到 YAML（线程安全，带文件锁）

        Args:
            data: 要保存的数据，None 时保存当前内存中的配置
        """
        if data is None:
            data = self._data

        os.makedirs(os.path.dirname(self._path), exist_ok=True)

        with self._lock:
            with file_lock(LOCK_FILE):
                with open(self._path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(
                        data,
                        f,
                        allow_unicode=True,
                        default_flow_style=False,
                        sort_keys=False,
                    )
        logger.info(f"配置已保存：{self._path}")

    def _merge_defaults(self, loaded: dict) -> dict:
        """深度合并默认配置"""
        result = self._deep_copy(DEFAULT_CONFIG)
        self._deep_update(result, loaded)
        return result

    @staticmethod
    def _deep_copy(data: dict) -> dict:
        """递归复制字典"""
        if isinstance(data, dict):
            return {k: ConfigManager._deep_copy(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [ConfigManager._deep_copy(item) for item in data]
        else:  # type: ignore[unreachable]
            return data

    @staticmethod
    def _deep_update(base: dict, overlay: dict):
        """深度更新 base，overlay 优先级更高"""
        for key, value in overlay.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                ConfigManager._deep_update(base[key], value)
            else:
                base[key] = value

    def is_loaded(self) -> bool:
        return self._loaded


# ==================== 配置单例 ====================
class Config:
    """
    配置单例，对外提供简洁的 get/set 接口

    用法：
        from app.config import config
        config.get("cfst.threads")            # 读取嵌套值，支持点号路径
        config.set("cfst.threads", 10)        # 写入（仅修改内存）
        config.save()                          # 持久化到文件
    """

    def __init__(self):
        self._manager = ConfigManager()
        self._data: dict = {}

    def init(self):
        """初始化配置（在 main.py 中调用一次）"""
        logger.info("正在初始化配置...")
        self._data = self._manager.load()
        logger.info(f"配置初始化完成，schema v{self._data.get('schema_version')}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        读取配置值，支持点号路径

        Examples:
            config.get("cfst.threads")            # -> 200
            config.get("scheduler.jobs.cfst.enabled")   # -> False

            config.get("nonexistent", default=0)   # -> 0
        """
        keys = key.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """
        设置配置值，支持点号路径（仅修改内存）

        Examples:
            config.set("cfst.threads", 10)
        """
        keys = key.split(".")
        target = self._data
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value

    def get_all(self) -> dict:
        """获取完整配置副本"""
        return self._manager._deep_copy(self._data)

    def update(self, data: dict):
        """批量更新配置（深度合并，仅修改内存）"""
        ConfigManager._deep_update(self._data, data)

    def save(self):
        """持久化当前配置到文件"""
        self._manager.save(self._data)

    def reload(self):
        """从文件重新加载配置"""
        self._data = self._manager.load()


# 全局单例
config = Config()
