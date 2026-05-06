"""
认证工具：密码哈希、Session 管理

所有模块通过以下方式验证登录：
    from app.auth import verify_session, verify_password, hash_password

Session 存储：本地 JSON 文件 + 内存缓存
密码存储：从 config.auth 读取，支持首次安装时初始化
"""
import hashlib
import json
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, Request

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Session 存储（生产环境应替换为 Redis）
SESSIONS_FILE = Path("cache") / "sessions.json"
_sessions: dict[str, dict] = {}
SESSION_TTL = timedelta(hours=24)


def _parse_created_at(value: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _save_sessions():
    try:
        SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SESSIONS_FILE.write_text(json.dumps(_sessions, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        logger.warning(f"保存会话缓存失败：{e}")


def _cleanup_expired_sessions(save: bool = True):
    expired_session_ids: list[str] = []
    now = datetime.now()

    for session_id, session in list(_sessions.items()):
        created_at = _parse_created_at(session.get("created_at", ""))
        if not created_at or now - created_at > SESSION_TTL:
            expired_session_ids.append(session_id)

    for session_id in expired_session_ids:
        _sessions.pop(session_id, None)

    if expired_session_ids and save:
        _save_sessions()


def _load_sessions():
    if not SESSIONS_FILE.exists():
        return

    try:
        loaded = json.loads(SESSIONS_FILE.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            _sessions.update(loaded)
        _cleanup_expired_sessions(save=False)
        logger.info(f"已加载 {len(_sessions)} 个本地会话")
    except Exception as e:
        logger.warning(f"加载本地会话失败：{e}")


_load_sessions()


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    PBKDF2-SHA256 哈希密码，返回 (hashed_password, salt)

    用途：
    - 注册/修改密码时调用
    - 验证密码时调用 verify_password(password, hash, salt)
    """
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return hashed.hex(), salt


def verify_password(password: str, hashed: str, salt: str) -> bool:
    """验证密码是否匹配"""
    expected, _ = hash_password(password, salt)
    return secrets.compare_digest(expected, hashed)


def create_session(user_id: str, username: str) -> str:
    """创建 session，返回 session_id"""
    session_id = secrets.token_urlsafe(32)
    _sessions[session_id] = {
        "user_id": user_id,
        "username": username,
        "created_at": datetime.now().isoformat(),
    }
    _save_sessions()
    logger.info(f"已为用户创建会话：{username}")
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    """获取 session，不存在或已过期返回 None"""
    session = _sessions.get(session_id)
    if not session:
        return None

    created_at = _parse_created_at(session.get("created_at", ""))
    if not created_at or datetime.now() - created_at > SESSION_TTL:
        delete_session(session_id)
        return None

    return session


def delete_session(session_id: str):
    """删除指定 session"""
    removed = _sessions.pop(session_id, None)
    if removed is not None:
        _save_sessions()


def clear_all_sessions():
    """清除所有 session（用于测试或安全事件）"""
    _sessions.clear()
    if SESSIONS_FILE.exists():
        try:
            SESSIONS_FILE.unlink()
        except Exception as e:
            logger.warning(f"删除会话缓存文件失败：{e}")
    logger.warning("已清除所有会话")


def is_initialized() -> bool:
    """
    检查是否已完成初始密码设置。
    config.auth.password_hash 为空时表示未初始化。
    """
    try:
        from app.config import config
        return bool(config.get("auth.password_hash"))
    except Exception:
        return False


def get_default_username() -> str:
    """获取默认用户名"""
    try:
        from app.config import config
        return config.get("auth.username", default="admin")
    except Exception:
        return "admin"


async def verify_session(request: Request) -> dict:
    """
    依赖注入：验证请求中的 session
    从 Cookie 或 Authorization Header 获取 session_id

    验证成功：返回 session dict {user_id, username, created_at}
    验证失败：抛出 HTTPException(401)
    """
    # 优先从 Cookie 获取
    session_id = request.cookies.get("session")

    # 其次从 Authorization Header 获取（格式：Bearer <session_id>）
    if not session_id:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            session_id = auth_header[7:]

    if not session_id:
        raise HTTPException(status_code=401, detail="未登录，请先登录")

    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="会话已过期，请重新登录")

    logger.debug(f"会话校验通过：{session['username']}")
    return session


def require_initialized(func):
    """
    装饰器：要求已完成初始密码设置
    未初始化时返回 403，引导用户设置密码
    """
    async def wrapper(*args, **kwargs):
        if not is_initialized():
            raise HTTPException(
                status_code=403,
                detail="未初始化，请先设置管理员密码",
            )
        return await func(*args, **kwargs)
    return wrapper
