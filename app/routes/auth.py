"""
认证路由：登录 / 登出 / CSRF / 初始化 / 版本

API 列表：
    POST /api/auth/login         - 登录（支持未初始化时设置初始密码）
    POST /api/auth/logout        - 登出
    GET  /api/auth/csrf          - 获取 CSRF token
    GET  /api/auth/status        - 获取当前登录状态
    GET  /api/version            - 获取版本信息
"""
import os
from fastapi import APIRouter, HTTPException, Response, Request, Depends
import secrets

from app.auth import (
    create_session,
    delete_session,
    verify_password,
    is_initialized,
    get_auth_state,
    get_default_username,
    verify_csrf_token,
    check_login_rate_limit,
    record_login_failure,
    reset_login_failures,
    get_client_ip,
    is_request_from_localhost,
    hash_password,
    mark_auth_initialized,
    auth_broken_detail,
    validate_password_strength,
    get_admin_reset_key,
    provision_admin_reset_artifacts,
)
from app.models import ApiResponse, LoginRequest, LoginResponse
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# HTTPS 反代场景下需要设置 secure=True，才能让 Cookie 只通过 HTTPS 传输
# 通过环境变量 COOKIE_SECURE=true 或 config.yaml app.https_proxy: true 激活
def _cookie_secure() -> bool:
    """
    判断是否应启用 Cookie Secure 属性。
    优先读环境变量 COOKIE_SECURE，其次读 config app.https_proxy。
    本地 HTTP 开发保持 false，HTTPS 反代生产环境应设为 true。
    """
    env_val = os.environ.get("COOKIE_SECURE", "").lower()
    if env_val in ("1", "true", "yes"):
        return True
    try:
        from app.config import config as _cfg
        return bool(_cfg.get("app.https_proxy", False))
    except Exception:
        return False


# ==================== 版本信息 ====================
@router.get("/version", response_model=ApiResponse)
async def get_version():
    """
    获取版本信息（供前端初始化检测）
    """
    from app import __version__
    return ApiResponse(data={"version": __version__}).model_dump()


@router.post("/login", response_model=ApiResponse)
async def login(req: LoginRequest, request: Request, response: Response, _csrf: None = Depends(verify_csrf_token)):
    """
    登录

    两种模式：
    1. 未初始化（config 中无密码）：将 req.password 作为初始密码设置
    2. 已初始化：验证用户名 + 密码后创建 session
    """
    from app.config import config

    # 速率限制：检查 IP 是否已被锁定
    client_ip = get_client_ip(request)
    check_login_rate_limit(client_ip)

    auth_state = get_auth_state()

    if auth_state == "BROKEN":
        logger.error(f"检测到损坏认证配置，拒绝登录：username={req.username}，来源 IP：{client_ip}")
        raise HTTPException(status_code=503, detail=auth_broken_detail())

    # 检查是否已初始化
    if auth_state == "UNINITIALIZED":
        allow_remote_init = os.environ.get("ALLOW_REMOTE_INIT", "false").lower() in ("1", "true", "yes")
        if not allow_remote_init and not is_request_from_localhost(request):
            logger.warning(f"拒绝非本地首次初始化请求：username={req.username}，来源 IP：{client_ip}")
            raise HTTPException(
                status_code=403,
                detail="服务尚未初始化。出于安全考虑，仅允许在本机访问完成首次管理员初始化；如确需远程初始化，请显式设置环境变量 ALLOW_REMOTE_INIT=true",
            )

        validate_password_strength(req.password)

        hashed, salt = hash_password(req.password)
        reset_key_hash = None
        reset_token_hash = None
        try:
            admin_reset_key = get_admin_reset_key()
            reset_key_hash, reset_token_hash = provision_admin_reset_artifacts(admin_reset_key)
        except ValueError:
            pass
        mark_auth_initialized(req.username, hashed, salt, reset_key_hash, reset_token_hash)
        config.save()

        session_id = create_session(user_id="1", username=req.username)
        response.set_cookie(
            key="session",
            value=session_id,
            httponly=True,
            samesite="lax",
            secure=_cookie_secure(),
        )

        reset_login_failures(client_ip)
        logger.info(f"初始化密码并创建会话：{req.username}")
        return ApiResponse(
            message="初始化完成，已登录",
            data={"user": {"username": req.username}}
        ).model_dump()

    # 已初始化：验证密码
    stored_username = get_default_username()
    stored_hash = config.get("auth.password_hash", default="")
    stored_salt = config.get("auth.password_salt", default="")

    # 用户名校验（支持修改用户名后仍能用 admin 登录）
    if req.username != stored_username:
        record_login_failure(client_ip)
        logger.warning(f"登录失败（用户名错误）：{req.username}，来源 IP：{client_ip}")
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not verify_password(req.password, stored_hash, stored_salt):
        record_login_failure(client_ip)
        logger.warning(f"登录失败（密码错误）：{req.username}，来源 IP：{client_ip}")
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 创建 session
    session_id = create_session(user_id="1", username=req.username)
    response.set_cookie(
        key="session",
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=_cookie_secure(),
    )

    reset_login_failures(client_ip)
    logger.info(f"用户登录成功：{req.username}，来源 IP：{client_ip}")
    return ApiResponse(
        message="登录成功",
        data={"user": {"username": req.username}}
    ).model_dump()


@router.post("/logout", response_model=ApiResponse)
async def logout(request: Request, response: Response, _csrf: None = Depends(verify_csrf_token)):
    """
    登出（无需登录，Cookie 无效时也返回成功）
    """
    session_id = request.cookies.get("session")
    if session_id:
        delete_session(session_id)
        logger.info(f"会话已登出：{session_id[:8]}...")
    response.delete_cookie("session")
    return ApiResponse(message="已登出").model_dump()


@router.get("/csrf", response_model=ApiResponse)
async def csrf(response: Response):
    """
    获取 CSRF token（双提交 Cookie 模式）

    流程：
    1. 服务端生成随机 token（32 字节 hex），写入 csrf_token Cookie（SameSite=Strict, HttpOnly=False）
    2. 前端 JS 读取该 Cookie，之后每个状态变更请求须在 X-CSRF-Token 头中携带相同 token
    3. 服务端用 verify_csrf_token(request) 依赖校验两者是否一致

    注意：HttpOnly=False 是必须的，让前端 JS 能读取 Cookie 值。
    """
    token = secrets.token_hex(32)
    response.set_cookie(
        key="csrf_token",
        value=token,
        httponly=False,   # 前端 JS 须能读取
        samesite="strict",
        max_age=3600,
        secure=_cookie_secure(),
    )
    return ApiResponse(data={"token": token}).model_dump()


@router.get("/status", response_model=ApiResponse)
async def get_auth_status(request: Request):
    """
    获取当前登录状态
    """
    session_id = request.cookies.get("session")
    if session_id:
        from app.auth import get_session
        session = get_session(session_id)
        if session:
            return ApiResponse(data={
                "logged_in": True,
                "username": session["username"],
                "initialized": is_initialized(),
                "auth_state": get_auth_state(),
            }).model_dump()

    return ApiResponse(data={
        "logged_in": False,
        "initialized": is_initialized(),
        "auth_state": get_auth_state(),
    }).model_dump()
