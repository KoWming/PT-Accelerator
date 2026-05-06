"""
PT-Accelerator 应用入口

Dockerfile: CMD ["python", "main.py"]
"""
import os
import uvicorn
import logging
from multiprocessing import freeze_support
from pathlib import Path

# 初始化日志（最先）
from app.utils.logger import setup_logging
setup_logging()

# 初始化配置
from app.config import config
config.init()

# 如果 config 中启用了 debug，调整日志级别
if config.get("app.debug", False):
    logging.getLogger().setLevel(logging.DEBUG)

RELOAD_EXCLUDES = [
    "logs/*",
    "dist/*",
    "cache/*",
    "CFST/*",
    "frontend/dist/*",
    "__pycache__/*",
    ".git/*",
]


def main() -> None:
    """启动 Web 服务。"""
    port = int(os.environ.get("APP_PORT", 23333))
    reload_enabled = config.get("app.debug", False)
    project_root = str(Path(__file__).resolve().parent)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload_enabled,
        reload_dirs=[project_root] if reload_enabled else None,
        reload_excludes=RELOAD_EXCLUDES if reload_enabled else None,
    )


if __name__ == "__main__":
    freeze_support()
    main()


