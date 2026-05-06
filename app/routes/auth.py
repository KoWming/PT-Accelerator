"""
认证路由：登录 / 登出 / CSRF / 初始化 / 版本

API 列表：
    POST /api/auth/login         - 登录（支持未初始化时设置初始密码）
    POST /api/auth/logout        - 登出
    GET  /api/auth/csrf          - 获取 CSRF token
    GET  /api/auth/status        - 获取当前登录状态
    GET  /api/version            - 获取版本信息
"""
from fastapi import APIRouter, HTTPException, Response, Request, Depends

from app.auth import (
    create_session,
    delete_session,
    verify_password,
    is_initialized,
    get_default_username,
    verify_session,
)
from app.models import ApiResponse, LoginRequest, LoginResponse
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


# ==================== 版本信息 ====================
@router.get("/version", response_model=ApiResponse)
async def get_version():
    """
    获取版本信息（供前端初始化检测）
    """
    from app import __version__
    return ApiResponse(data={"version": __version__}).model_dump()


@router.post("/login", response_model=ApiResponse)
async def login(req: LoginRequest, response: Response):
    """
    登录

    两种模式：
    1. 未初始化（config 中无密码）：将 req.password 作为初始密码设置
    2. 已初始化：验证用户名 + 密码后创建 session
    """
    from app.config import config

    # 检查是否已初始化
    if not is_initialized():
        # 首次安装：设置初始密码
        from app.auth import hash_password

        if len(req.password) < 4:
            raise HTTPException(status_code=400, detail="密码长度不能少于 4 位")

        hashed, salt = hash_password(req.password)
        config.set("auth.username", req.username)
        config.set("auth.password_hash", hashed)
        config.set("auth.password_salt", salt)
        config.save()

        session_id = create_session(user_id="1", username=req.username)
        response.set_cookie(key="session", value=session_id, httponly=True, samesite="lax")

        logger.info(f"初始化密码并创建会话：{req.username}")
        return ApiResponse(
            message="初始化完成，已登录",
            data={"token": session_id, "user": {"username": req.username}}
        ).model_dump()

    # 已初始化：验证密码
    stored_username = get_default_username()
    stored_hash = config.get("auth.password_hash", default="")
    stored_salt = config.get("auth.password_salt", default="")

    # 用户名校验（支持修改用户名后仍能用 admin 登录）
    if req.username != stored_username:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not verify_password(req.password, stored_hash, stored_salt):
        logger.warning(f"登录失败：{req.username}")
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 创建 session
    session_id = create_session(user_id="1", username=req.username)
    response.set_cookie(key="session", value=session_id, httponly=True, samesite="lax")

    logger.info(f"用户登录成功：{req.username}")
    return ApiResponse(
        message="登录成功",
        data={"token": session_id, "user": {"username": req.username}}
    ).model_dump()


@router.post("/logout", response_model=ApiResponse)
async def logout(request: Request, response: Response):
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
async def csrf():
    """
    获取 CSRF token
    TODO: 实现服务端 CSRF token 存储和验证
    """
    return ApiResponse(data={"token": "TODO", "note": "CSRF token 待实现"}).model_dump()


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
            }).model_dump()

    return ApiResponse(data={
        "logged_in": False,
        "initialized": is_initialized(),
        "default_username": get_default_username(),
    }).model_dump()
