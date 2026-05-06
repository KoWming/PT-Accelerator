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

from app.auth import verify_session, hash_password, verify_password, is_initialized
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
    sensitive_keys = {"password", "password_hash", "token", "secret", "api_key"}

    def _mask_recursive(d: dict):
        for key, value in d.items():
            lower_key = key.lower()
            if any(sk in lower_key for sk in sensitive_keys):
                d[key] = "********"
            elif isinstance(value, dict):
                _mask_recursive(value)

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
            "config_version": config.get("schema_version"),
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
async def update_config(request: dict, session: dict = Depends(verify_session)):
    """
    批量更新配置（深度合并，不支持删除字段）
    """
    logger.info(f"用户正在更新配置：{session['username']}")

    # 逐个验证点号路径是否合法
    valid_toplevel = {
        "app", "auth", "cfst", "hosts", "trackers", "cloudflare_domains",
        "downloaders", "scheduler", "backup", "notify", "ikuai", "mihosts",
    }


    errors = []
    for key in request.keys():
        if key not in valid_toplevel:
            errors.append(f"不支持的配置节: {key}")

    if errors:
        raise HTTPException(status_code=400, detail="; ".join(errors))

    # 深度合并到内存配置
    config.update(request)
    config.save()

    logger.info(f"配置更新完成，操作用户：{session['username']}")
    return ApiResponse(message="配置已更新").model_dump()


@router.put("/password", response_model=ApiResponse)
async def change_password(
    req: PasswordChangeRequest,
    session: dict = Depends(verify_session),
):
    """
    修改管理员密码

    - 未初始化时：设置初始密码
    - 已初始化时：验证旧密码后修改
    """
    logger.info(f"收到修改密码请求，操作用户：{session['username']}")

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
    config.set("auth.password_hash", new_hash)
    config.set("auth.password_salt", new_salt)
    config.save()

    logger.info(f"密码修改成功，操作用户：{session['username']}")
    return ApiResponse(message="密码已修改").model_dump()
