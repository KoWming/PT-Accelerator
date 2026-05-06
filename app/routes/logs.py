"""
系统日志路由

API 列表：
    GET  /api/logs          - 获取日志内容
    POST /api/logs/clear    - 清空日志
"""
import os
from fastapi import APIRouter, Query

from app.models import ApiResponse
from app.utils.logger import get_logger, LOG_FILE

router = APIRouter()
logger = get_logger(__name__)


@router.get("/logs", response_model=ApiResponse)
async def get_logs(
    lines: int = Query(default=1000, ge=1, le=10000, description="返回最近 N 行日志"),
):
    """
    获取系统日志（从后向前读取指定行数）
    """
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
async def clear_logs():
    """
    清空日志文件
    """
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write("")
        logger.info("日志已清空")
        return ApiResponse(message="日志已清空").model_dump()
    except Exception as e:
        logger.error(f"清空日志失败：{e}")
        return ApiResponse(message="清空失败", code=1).model_dump()
