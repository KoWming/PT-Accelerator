"""
系统日志路由

API 列表：
    GET  /api/logs          - 获取日志内容（需登录）
    POST /api/logs/clear    - 清空日志（需登录）
"""
import os
from fastapi import APIRouter, Depends, Query

from app.auth import verify_session, verify_csrf_token
from app.models import ApiResponse
from app.utils.logger import get_logger, LOG_FILE

router = APIRouter()
logger = get_logger(__name__)


@router.get("/logs", response_model=ApiResponse)
async def get_logs(
    lines: int = Query(default=1000, ge=1, le=10000, description="返回最近 N 行日志"),
    session: dict = Depends(verify_session),
):
    """
    获取系统日志（从后向前读取指定行数）
    需要登录认证。
    """
    _ = session  # 鉴权通过后无需使用
    try:
        if not os.path.exists(LOG_FILE):
            return ApiResponse(data={"logs": ""}).model_dump()

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            all_lines = f.readlines()

        # 从后向前取 N 行
        recent_lines = all_lines[-lines:] if lines < len(all_lines) else all_lines
        logs_content = "".join(recent_lines)

        return ApiResponse(data={"logs": logs_content}).model_dump()
    except Exception as e:
        logger.error(f"读取日志失败：{e}")
        return ApiResponse(data={"logs": ""}).model_dump()


@router.post("/logs/clear", response_model=ApiResponse)
async def clear_logs(
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    清空日志文件
    需要登录认证。
    """
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write("")
        logger.warning(f"日志已被清空，操作用户：{session['username']}")
        return ApiResponse(message="日志已清空").model_dump()
    except Exception as e:
        logger.error(f"清空日志失败：{e}")
        return ApiResponse(message="清空失败", code=1).model_dump()
