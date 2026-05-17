"""
认证工具：密码哈希、Session 管理、登录速率限制

所有模块通过以下方式验证登录：
    from app.auth import verify_session, verify_password, hash_password

Session 存储：本地 JSON 文件 + 内存缓存
密码存储：从 config.auth 读取，支持首次安装时初始化
速率限制：per-IP 失败次数 + 指数退避锁定，防暴力破解
"""
import hashlib
import ipaddress
import json
import os
import re
import secrets
import stat
import yaml
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Literal

from fastapi import HTTPException, Request

from app.utils.logger import get_logger

logger = get_logger(__name__)
AuthState = Literal["UNINITIALIZED", "INITIALIZED", "BROKEN"]


# 每个 IP 允许的最大连续失败次数，超出后锁定
_LOGIN_MAX_FAILURES = int(os.environ.get("LOGIN_MAX_FAILURES", "5"))
# 锁定持续时间（秒），默认 5 分钟
_LOGIN_LOCKOUT_SECONDS = int(os.environ.get("LOGIN_LOCKOUT_SECONDS", "300"))

# 内存中维护各 IP 的失败记录 {ip: {"count": int, "locked_until": datetime | None, "last_fail": datetime}}
_login_failures: dict[str, dict] = defaultdict(lambda: {"count": 0, "locked_until": None, "last_fail": None})
_login_lock = __import__("threading").Lock()


def get_client_ip(request: Request) -> str:
    """
    获取真实客户端 IP。

    默认仅信任直连对端地址 request.client.host。
    只有当请求来源本身属于受信任代理时，才解析 X-Forwarded-For / X-Real-IP。
    """
    trusted_proxy_ips = {
        ip.strip() for ip in str(os.environ.get("TRUSTED_PROXY_IPS", "") or "").split(",") if ip.strip()
    }

    direct_ip = request.client.host if request.client else "unknown"
    if direct_ip == "unknown":
        return direct_ip

    if direct_ip not in trusted_proxy_ips:
        return direct_ip

    xff = request.headers.get("X-Forwarded-For")
    if xff:
        forwarded_ip = xff.split(",")[0].strip()
        if forwarded_ip:
            return forwarded_ip

    xri = request.headers.get("X-Real-IP")
    if xri:
        forwarded_ip = xri.strip()
        if forwarded_ip:
            return forwarded_ip

    return direct_ip


def is_request_from_localhost(request: Request) -> bool:
    """
    判断请求是否来自本机回环地址。
    仅允许 localhost/127.0.0.1/::1 等本地来源用于高敏感初始化流程。
    """
    client_ip = get_client_ip(request)
    try:
        return ipaddress.ip_address(client_ip).is_loopback
    except ValueError:
        return client_ip in {"localhost", "::1"}


def check_login_rate_limit(ip: str) -> None:
    """
    检查 IP 是否已被锁定。若锁定则抛出 429；否则通过。
    在登录失败时应调用 record_login_failure(ip)，成功时调用 reset_login_failures(ip)。
    """
    with _login_lock:
        record = _login_failures[ip]
        locked_until = record.get("locked_until")
        if locked_until and datetime.now() < locked_until:
            remaining = int((locked_until - datetime.now()).total_seconds())
            raise HTTPException(
                status_code=429,
                detail=f"登录尝试过于频繁，账号已临时锁定，请 {remaining} 秒后重试",
                headers={"Retry-After": str(remaining)},
            )
        # 锁定已到期，自动解锁
        if locked_until and datetime.now() >= locked_until:
            record["count"] = 0
            record["locked_until"] = None


def record_login_failure(ip: str) -> None:
    """登录失败时递增计数器；超阈值则锁定 IP。"""
    with _login_lock:
        record = _login_failures[ip]
        record["count"] += 1
        record["last_fail"] = datetime.now()
        if record["count"] >= _LOGIN_MAX_FAILURES:
            record["locked_until"] = datetime.now() + timedelta(seconds=_LOGIN_LOCKOUT_SECONDS)
            logger.warning(
                f"IP {ip} 连续登录失败 {record['count']} 次，已锁定 {_LOGIN_LOCKOUT_SECONDS} 秒"
            )


def reset_login_failures(ip: str) -> None:
    """登录成功时清零对应 IP 的失败计数。"""
    with _login_lock:
        _login_failures.pop(ip, None)


# ==================== CSRF 验证 ====================


async def verify_csrf_token(request: Request) -> None:
    """
    依赖注入：校验 CSRF token（双提交 Cookie 模式）

    规则：
    - 仅对状态变更方法（POST / PUT / PATCH / DELETE）做校验
    - GET / HEAD / OPTIONS 直接放行
    - 从请求头 X-CSRF-Token 取 token，与 Cookie csrf_token 做常量时间比较

    用法（在需要 CSRF 保护的路由上添加）：
        from app.auth import verify_session, verify_csrf_token
        from fastapi import Depends

        @router.post("/sensitive")
        async def handler(
            session=Depends(verify_session),
            _=Depends(verify_csrf_token),
        ):
            ...
    """
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return

    cookie_token = request.cookies.get("csrf_token", "")
    header_token = request.headers.get("X-CSRF-Token", "")

    if not cookie_token or not header_token:
        raise HTTPException(
            status_code=403,
            detail="CSRF 验证失败：缺少 CSRF token，请先调用 GET /api/auth/csrf 获取 token",
        )

    if not secrets.compare_digest(cookie_token, header_token):
        logger.warning(
            f"CSRF 验证失败：Cookie token 与请求头 token 不一致，路径={request.url.path}"
        )
        raise HTTPException(status_code=403, detail="CSRF 验证失败：token 不匹配")

# Session 存储（生产环境应替换为 Redis）
SESSIONS_FILE = Path("cache") / "sessions.json"
AUTH_STATE_MARKER = Path(os.environ.get("CONFIG_DIR", "config")) / ".auth_initialized"
ADMIN_RESET_TOKEN_FILE = Path(os.environ.get("CONFIG_DIR", "config")) / ".admin_reset_token"
_sessions: dict[str, dict] = {}
SESSION_TTL = timedelta(hours=24)


def _write_private_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except (OSError, NotImplementedError):
        pass


def _touch_auth_state_marker() -> None:
    try:
        _write_private_text_file(AUTH_STATE_MARKER, datetime.now().isoformat())
    except Exception as exc:
        logger.warning(f"写入认证初始化标记失败：{exc}")


def _hash_reset_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_admin_reset_token() -> str:
    try:
        if not ADMIN_RESET_TOKEN_FILE.exists():
            raise ValueError("缺少管理员恢复令牌文件")
        token = ADMIN_RESET_TOKEN_FILE.read_text(encoding="utf-8").strip()
        if not token:
            raise ValueError("管理员恢复令牌文件为空")
        return token
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"读取管理员恢复令牌文件失败：{exc}") from exc


def get_admin_reset_key() -> str:
    reset_key = str(os.environ.get("ADMIN_RESET_KEY", "") or "").strip()
    if not reset_key:
        raise ValueError("缺少 ADMIN_RESET_KEY 环境变量，已拒绝离线管理员重置")
    return reset_key


def provision_admin_reset_artifacts(reset_key: str) -> tuple[str, str]:
    normalized_key = str(reset_key or "").strip()
    if not normalized_key:
        raise ValueError("管理员恢复密钥不能为空")

    try:
        token = read_admin_reset_token()
    except ValueError:
        token = secrets.token_urlsafe(32)
        try:
            _write_private_text_file(ADMIN_RESET_TOKEN_FILE, token)
        except Exception as exc:
            raise ValueError(f"写入管理员恢复令牌文件失败：{exc}") from exc

    return _hash_reset_secret(normalized_key), _hash_reset_secret(token)


def verify_admin_reset_access(reset_key: str) -> None:
    from app.config import config

    normalized_key = str(reset_key or "").strip()
    configured_key = get_admin_reset_key()
    if not secrets.compare_digest(configured_key, normalized_key):
        raise ValueError("管理员恢复密钥无效，已拒绝离线管理员重置")

    stored_key_hash = str(config.get("auth.reset_key_hash", default="") or "").strip()
    stored_token_hash = str(config.get("auth.reset_token_hash", default="") or "").strip()
    if not stored_key_hash or not stored_token_hash:
        raise ValueError("当前部署尚未完成离线恢复材料配置，请先在已登录状态下设置 ADMIN_RESET_KEY 并完成一次密码修改")

    if not secrets.compare_digest(_hash_reset_secret(normalized_key), stored_key_hash):
        raise ValueError("管理员恢复密钥无效，已拒绝离线管理员重置")

    token = read_admin_reset_token()
    if not secrets.compare_digest(_hash_reset_secret(token), stored_token_hash):
        raise ValueError("本机管理员恢复令牌无效，已拒绝离线管理员重置")


def _read_auth_state_marker() -> str:
    try:
        if AUTH_STATE_MARKER.exists():
            return AUTH_STATE_MARKER.read_text(encoding="utf-8").strip()
    except Exception as exc:
        logger.warning(f"读取认证初始化标记失败：{exc}")
    return ""


def _parse_created_at(value: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _save_sessions():
    try:
        SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SESSIONS_FILE.write_text(json.dumps(_sessions, ensure_ascii=False, indent=2), encoding="utf-8")
        # 设置文件权限为 0o600（仅 owner 可读写），防止本地用户读取有效 Session
        try:
            SESSIONS_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)
        except (OSError, NotImplementedError):
            # Windows 上 chmod 语义不同，忽略失败
            pass
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
        if _sessions:
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


def revoke_user_sessions(username: str) -> int:
    """撤销指定用户的所有会话，返回被撤销的会话数"""
    to_remove = [
        sid for sid, s in _sessions.items()
        if s.get("username") == username
    ]
    for sid in to_remove:
        _sessions.pop(sid, None)
    if to_remove:
        _save_sessions()
        logger.info(f"已撤销用户 {username} 的 {len(to_remove)} 个旧会话")
    return len(to_remove)


def create_session(user_id: str, username: str) -> str:
    """创建 session，返回 session_id（单会话模式：新登录自动踢掉该用户旧会话）"""
    revoke_user_sessions(username)
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


def get_auth_state() -> AuthState:
    """
    获取认证状态。

    - UNINITIALIZED: 从未初始化，允许首次设置管理员密码
    - INITIALIZED: 认证配置完整，可正常登录
    - BROKEN: 认证配置缺失/半缺失/被篡改，必须拒绝在线初始化并走离线恢复
    """
    try:
        from app.config import config

        username = str(config.get("auth.username", default="") or "").strip()
        password_hash = str(config.get("auth.password_hash", default="") or "").strip()
        password_salt = str(config.get("auth.password_salt", default="") or "").strip()
        initialized = bool(config.get("auth.initialized", default=False))
        initialized_at = str(config.get("auth.initialized_at", default="") or "").strip()
        marker_value = _read_auth_state_marker()
    except Exception:
        return "BROKEN"

    has_hash = bool(password_hash)
    has_salt = bool(password_salt)
    has_init_marker = initialized or bool(initialized_at) or bool(marker_value)

    if has_hash and has_salt:
        if not marker_value:
            _touch_auth_state_marker()
        return "INITIALIZED"

    if has_hash != has_salt:
        return "BROKEN"

    if has_init_marker:
        return "BROKEN"

    return "UNINITIALIZED"


def is_initialized() -> bool:
    """
    检查是否已完成初始密码设置。
    仅在认证状态完整时返回 True。
    """
    return get_auth_state() == "INITIALIZED"


def mark_auth_initialized(
    username: str,
    password_hash: str,
    password_salt: str,
    reset_key_hash: Optional[str] = None,
    reset_token_hash: Optional[str] = None,
) -> None:
    """写入完整认证元数据。"""
    from app.config import config

    config.set("auth.username", username)
    config.set("auth.password_hash", password_hash)
    config.set("auth.password_salt", password_salt)
    config.set("auth.initialized", True)
    config.set("auth.initialized_at", datetime.now().isoformat())
    if reset_key_hash is not None:
        config.set("auth.reset_key_hash", reset_key_hash)
    if reset_token_hash is not None:
        config.set("auth.reset_token_hash", reset_token_hash)
    _touch_auth_state_marker()


def auth_broken_detail() -> str:
    return "认证配置损坏或疑似被篡改，已禁止在线初始化/登录。请在服务器本机执行管理员离线重置恢复认证配置。"


def validate_password_strength(password: str) -> None:
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="密码长度不能少于 8 位，且须同时包含字母和数字")
    if len(password) > 128:
        raise HTTPException(status_code=400, detail="密码长度不能超过 128 位")
    if not re.search(r"[A-Za-z]", password):
        raise HTTPException(status_code=400, detail="密码必须包含至少一个字母")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="密码必须包含至少一个数字")


def clear_all_sessions():
    """清除所有 session（用于测试或安全事件）"""
    _sessions.clear()
    if SESSIONS_FILE.exists():
        try:
            SESSIONS_FILE.unlink()
        except Exception as e:
            logger.warning(f"删除会话缓存文件失败：{e}")
    logger.warning("已清除所有会话")


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
    仅从 HttpOnly Cookie 获取 session_id。

    验证成功：返回 session dict {user_id, username, created_at}
    验证失败：抛出 HTTPException(401)
    """
    auth_state = get_auth_state()
    if auth_state == "BROKEN":
        raise HTTPException(status_code=503, detail=auth_broken_detail())

    session_id = request.cookies.get("session")
    if not session_id:
        raise HTTPException(status_code=401, detail="未登录，请先登录")

    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="会话已过期，请重新登录")

    logger.debug(f"会话校验通过：{session['username']}")
    return session




def reset_admin_password(username: str, new_password: str, reset_key: str) -> None:
    """本机离线重置管理员账号与密码。"""
    reset_key = str(reset_key or "").strip()
    verify_admin_reset_access(reset_key)

    username = str(username or "").strip()
    if not username:
        raise ValueError("管理员用户名不能为空")

    try:
        validate_password_strength(new_password)
    except HTTPException as exc:
        raise ValueError(exc.detail) from exc

    password_hash, password_salt = hash_password(new_password)
    reset_key_hash, reset_token_hash = provision_admin_reset_artifacts(reset_key)

    from app.config import CONFIG_PATH, ConfigManager, config

    manager = ConfigManager(CONFIG_PATH)
    current_data = config.get_all() if getattr(config, "_data", None) else manager.load()
    auth_section = current_data.setdefault("auth", {})
    auth_section["username"] = username
    auth_section["password_hash"] = password_hash
    auth_section["password_salt"] = password_salt
    auth_section["initialized"] = True
    auth_section["initialized_at"] = datetime.now().isoformat()
    auth_section["reset_key_hash"] = reset_key_hash
    auth_section["reset_token_hash"] = reset_token_hash
    manager.save(current_data)
    config.reload()
    clear_all_sessions()
    logger.warning(f"管理员凭据已通过离线恢复流程重置：{username}")


def require_initialized(func):
    """
    装饰器：要求已完成初始密码设置
    未初始化或认证损坏时直接拒绝。
    """
    async def wrapper(*args, **kwargs):
        auth_state = get_auth_state()
        if auth_state == "BROKEN":
            raise HTTPException(status_code=503, detail=auth_broken_detail())
        if auth_state != "INITIALIZED":
            raise HTTPException(
                status_code=403,
                detail="未初始化，请先设置管理员密码",
            )
        return await func(*args, **kwargs)
    return wrapper
