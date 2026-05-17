"""
全局设置路由：配置读写、密码修改

API 列表：
    GET  /api/settings/info       - 系统信息（版本、运行时间）
    GET  /api/settings/config    - 获取完整配置（脱敏）
    PUT  /api/settings/config    - 批量更新配置
    PUT  /api/settings/password   - 修改管理员密码
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.auth import (
    verify_session,
    verify_password,
    is_initialized,
    get_auth_state,
    verify_csrf_token,
    auth_broken_detail,
    mark_auth_initialized,
    hash_password,
    get_admin_reset_key,
    provision_admin_reset_artifacts,
    revoke_user_sessions,
)
from app.config import config
from app.models import (
    ApiResponse,
    PasswordChangeRequest,
    HealthResponse,
)
from app.utils.logger import get_logger
from app import __version__

router = APIRouter()
logger = get_logger(__name__)

# 启动时间（模块加载时记录）
_start_time = datetime.now()


def _mask_passwords(cfg: dict) -> dict:
    """
    配置脱敏：隐藏所有 password 相关字段的明文
    """
    import copy

    result = copy.deepcopy(cfg)
    sensitive_keys = {"password", "password_hash", "token", "secret", "api_key", "apikey", "reset_key"}

    def _mask_recursive(value):
        if isinstance(value, dict):
            for key, item in value.items():
                lower_key = key.lower()
                if any(sk in lower_key for sk in sensitive_keys):
                    value[key] = "********"
                else:
                    _mask_recursive(item)
        elif isinstance(value, list):
            for item in value:
                _mask_recursive(item)

    _mask_recursive(result)
    return result


@router.get("/info", response_model=ApiResponse)
async def get_system_info(session: dict = Depends(verify_session)):
    """
    获取系统信息（版本、运行时间、平台）
    """
    uptime_seconds = (datetime.now() - _start_time).total_seconds()
    days, remainder = divmod(int(uptime_seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        uptime_str = f"{days}天 {hours}时 {minutes}分"
    elif hours > 0:
        uptime_str = f"{hours}时 {minutes}分 {seconds}秒"
    else:
        uptime_str = f"{minutes}分 {seconds}秒"

    return ApiResponse(
        data={
            "version": __version__,
            "uptime": uptime_str,
            "uptime_seconds": int(uptime_seconds),
            "platform": "Windows" if __import__("os").name == "nt" else "Linux",
            "initialized": is_initialized(),
            "auth_state": get_auth_state(),
            "config_version": config.get("schema_version"),
            "offline_reset_supported": bool(
                str(config.get("auth.reset_key_hash", default="") or "").strip()
                and str(config.get("auth.reset_token_hash", default="") or "").strip()
            ),
        }
    ).model_dump()


@router.get("/config", response_model=ApiResponse)
async def get_config(session: dict = Depends(verify_session)):
    """
    获取完整配置（密码等敏感字段已脱敏）
    """
    full_config = config.get_all()
    masked_config = _mask_passwords(full_config)
    return ApiResponse(data=masked_config).model_dump()


@router.put("/config", response_model=ApiResponse)
async def update_config(
    request: dict,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    批量更新配置（深度合并，不支持删除字段）
    """
    logger.info(f"用户正在更新配置：{session['username']}")

    # 逐个验证顶层配置节是否合法
    # 注意：auth 节仅允许通过此接口修改 username；
    # password_hash / password_salt 等敏感字段仍禁止走该接口，
    # 密码修改须通过 PUT /api/settings/password 进行校验
    auth_payload = request.get("auth")
    if auth_payload is not None:
        if not isinstance(auth_payload, dict):
            raise HTTPException(status_code=400, detail="auth 配置必须为对象")

        unsupported_auth_keys = [key for key in auth_payload.keys() if key != "username"]
        if unsupported_auth_keys:
            raise HTTPException(status_code=400, detail="auth 节仅允许修改 username")

        username = str(auth_payload.get("username") or "").strip()
        if not username:
            raise HTTPException(status_code=400, detail="管理员用户名不能为空")

        config.set("auth.username", username)

    valid_toplevel = {
        "app", "cfst", "hosts",
        "downloaders", "scheduler", "backup", "notify", "ikuai", "mihosts",
    }

    update_payload = {
        key: value
        for key, value in request.items()
        if key != "auth"
    }

    errors = []
    for key in update_payload.keys():
        if key not in valid_toplevel:
            errors.append(f"不支持的配置节: {key}")

    if errors:
        raise HTTPException(status_code=400, detail="; ".join(errors))

    # 深度合并到内存配置
    if update_payload:
        config.update(update_payload)
    config.save()

    logger.info(f"配置更新完成，操作用户：{session['username']}")
    return ApiResponse(message="配置已更新").model_dump()


@router.put("/password", response_model=ApiResponse)
async def change_password(
    req: PasswordChangeRequest,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    修改管理员密码

    - 未初始化时：设置初始密码
    - 已初始化时：验证旧密码后修改
    """
    logger.info(f"收到修改密码请求，操作用户：{session['username']}")

    auth_state = get_auth_state()
    if auth_state == "BROKEN":
        logger.error(f"认证配置损坏时拒绝在线改密，操作用户：{session['username']}")
        raise HTTPException(status_code=503, detail=auth_broken_detail())

    # 获取当前密码哈希
    stored_hash = config.get("auth.password_hash", default="")
    stored_salt = config.get("auth.password_salt", default="")

    if stored_hash and stored_salt:
        # 已初始化：验证旧密码
        if not req.old_password:
            raise HTTPException(status_code=400, detail="请输入当前密码")
        if not verify_password(req.old_password, stored_hash, stored_salt):
            logger.warning(f"旧密码校验失败，操作用户：{session['username']}")
            raise HTTPException(status_code=400, detail="旧密码错误")


    # 设置新密码
    new_hash, new_salt = hash_password(req.new_password)
    reset_key_hash = None
    reset_token_hash = None
    try:
        admin_reset_key = get_admin_reset_key()
        reset_key_hash, reset_token_hash = provision_admin_reset_artifacts(admin_reset_key)
    except ValueError:
        pass
    mark_auth_initialized(session["username"], new_hash, new_salt, reset_key_hash, reset_token_hash)
    config.save()

    # 改密码后撤销该用户所有旧会话（包括当前会话），需重新登录
    revoked = revoke_user_sessions(session["username"])
    if revoked:
        logger.info(f"密码修改后已撤销 {revoked} 个旧会话，需重新登录")

    logger.info(f"密码修改成功，操作用户：{session['username']}")
    return ApiResponse(message="密码已修改，请重新登录").model_dump()
