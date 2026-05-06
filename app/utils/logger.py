"""
统一日志接口
所有业务模块使用 from app.utils.logger import get_logger 获取 logger
禁止直接 import logging
"""
import logging
import os
from logging.handlers import TimedRotatingFileHandler

# 日志输出配置（集中定义）
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 轮转策略：按天切分，保留 5 个备份
BACKUP_COUNT = 5
WHEN = "midnight"
INTERVAL = 1

# 第三方 logger 抑制配置
THIRD_PARTY_LEVELS = {
    "apscheduler": logging.WARNING,
    "uvicorn": logging.WARNING,
    "uvicorn.access": logging.WARNING,
    "uvicorn.error": logging.WARNING,
    "httpx": logging.WARNING,
    "httpcore": logging.WARNING,
    "watchfiles": logging.WARNING,
    "watchfiles.main": logging.WARNING,
    "asyncio": logging.WARNING,
    "tzlocal": logging.WARNING,
}


_configured = False


def setup_logging():
    """
    全局日志初始化
    由 main.py 启动时调用一次，确保所有模块在日志系统就绪后才开始工作
    """
    global _configured
    if _configured:
        return

    os.makedirs(LOG_DIR, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # 清除已有的 handler（避免重复）
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    # 文件 handler：按天轮转
    file_handler = TimedRotatingFileHandler(
        LOG_FILE,
        when=WHEN,
        interval=INTERVAL,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    root_logger.addHandler(file_handler)

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    root_logger.addHandler(console_handler)

    # 第三方 logger 抑制
    for name, level in THIRD_PARTY_LEVELS.items():
        logging.getLogger(name).setLevel(level)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    所有业务模块获取 logger 的统一入口
    使用示例：
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
    """
    return logging.getLogger(name)
