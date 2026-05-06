"""
配置读写（带文件锁，防止并发写坏 YAML）
TODO Phase 3：从此文件替代 globals.py 的配置读写逻辑
"""
import os
import yaml
from pathlib import Path
from threading import Lock

from app.utils.logger import get_logger
from app.utils.file_lock import file_lock

logger = get_logger(__name__)

CONFIG_PATH = os.environ.get("CONFIG_PATH", "config/config.yaml")


class ConfigManager:
    """线程安全的配置文件读写"""

    def __init__(self, path: str = CONFIG_PATH):
        self._path = path
        self._lock = Lock()
        self._data: dict = {}
        self.load()

    def load(self):
        """从 YAML 加载配置"""
        with self._lock:
            if os.path.exists(self._path):
                with open(self._path, "r", encoding="utf-8") as f:
                    self._data = yaml.safe_load(f) or {}
                logger.info(f"配置已加载：{self._path}")
            else:
                self._data = {}
                logger.warning(f"配置文件不存在：{self._path}")

    def save(self):
        """保存配置到 YAML（带文件锁）"""
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with self._lock:
            with file_lock(self._path + ".lock"):
                with open(self._path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(self._data, f, allow_unicode=True, default_flow_style=False)
        logger.info(f"配置已保存：{self._path}")

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        self._data[key] = value

    def update(self, data: dict):
        self._data.update(data)

    def all(self) -> dict:
        return self._data.copy()


# 全局实例
config_manager = ConfigManager()
