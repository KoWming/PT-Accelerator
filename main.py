"""
PT-Accelerator 应用入口

Dockerfile: CMD ["python", "main.py"]
"""
import argparse
import getpass
import os
import sys
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

logger = logging.getLogger(__name__)
OFFLINE_RESET_LOG_PREFIX = "[offline-reset]"

RELOAD_EXCLUDES = [
    "logs/*",
    "dist/*",
    "cache/*",
    "CFST/*",
    "frontend/dist/*",
    "__pycache__/*",
    ".git/*",
]


def run_server() -> None:
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


def reset_admin_cli(username: str) -> int:
    from app.auth import get_admin_reset_key, reset_admin_password

    try:
        reset_key = get_admin_reset_key()
        password = getpass.getpass("请输入新的管理员密码: ")
        password_confirm = getpass.getpass("请再次输入新的管理员密码: ")
        if password != password_confirm:
            logger.error(f"{OFFLINE_RESET_LOG_PREFIX} 两次输入的新密码不一致，已取消离线重置")
            return 1

        reset_admin_password(username=username, new_password=password, reset_key=reset_key)
    except ValueError as exc:
        logger.error(f"{OFFLINE_RESET_LOG_PREFIX} {exc}")
        return 1

    print("管理员凭据已离线重置，现有会话已清空。")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="PT-Accelerator 启动与维护入口")
    parser.add_argument("--reset-admin", action="store_true", help="在服务器本机离线重置管理员账号与密码（需配置 ADMIN_RESET_KEY 且本机存在恢复令牌文件）")
    parser.add_argument("--username", default="admin", help="离线重置时使用的管理员用户名")
    args = parser.parse_args()

    if args.reset_admin:
        return reset_admin_cli(username=args.username)

    run_server()
    return 0


if __name__ == "__main__":
    freeze_support()
    sys.exit(main())



