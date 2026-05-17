"""
通知路由：渠道管理、测试发送
"""
from fastapi import APIRouter, Depends, HTTPException

from app.auth import verify_session, verify_csrf_token
from app.models import (
    ApiResponse,
    NotifyChannelIn,
    NotifyChannelOut,
    NotifyChannelListOut,
    NotifyChannelCreateOut,
    NotifyChannelUpdateOut,
    NotifyChannelDeleteOut,
)
from app.services.notify_service import notify_service
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


# ==================== 渠道 CRUD ====================


@router.get("/", response_model=ApiResponse)
async def list_channels(session: dict = Depends(verify_session)):
    """
    列出所有通知渠道
    """
    channels = notify_service.list_channels()
    return ApiResponse(
        data=NotifyChannelListOut(
            channels=channels,
            total=len(channels),
        ).model_dump()
    ).model_dump()


@router.get("/types", response_model=ApiResponse)
async def get_channel_types(session: dict = Depends(verify_session)):
    """
    获取支持的渠道类型
    """
    types = notify_service.get_supported_types()
    return ApiResponse(data={"types": types}).model_dump()


@router.post("/", response_model=ApiResponse)
async def add_channel(
    req: NotifyChannelIn,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    添加新的通知渠道

    - 类型无效返回 400
    - 名称为空返回 400
    - 名称重复返回 409
    """
    try:
        channel = notify_service.add_channel(
            name=req.name,
            channel_type=req.type,
            config=req.config or {},
            enabled=req.enabled,
        )
        logger.info(f"通知渠道已添加，操作用户：{session['username']}，名称：{channel['name']}")
        return ApiResponse(
            data=NotifyChannelCreateOut(id=channel["id"]).model_dump()
        ).model_dump()
    except ValueError as e:
        msg = str(e)
        if "已存在" in msg:
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=400, detail=msg)


@router.get("/{channel_id}", response_model=ApiResponse)
async def get_channel(channel_id: str, session: dict = Depends(verify_session)):
    """
    获取单个通知渠道
    """
    channel = notify_service.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail=f"渠道不存在: {channel_id}")
    return ApiResponse(data=channel).model_dump()


@router.put("/{channel_id}", response_model=ApiResponse)
async def update_channel(
    channel_id: str,
    req: NotifyChannelIn,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    更新通知渠道

    - 渠道不存在返回 404
    - 类型无效返回 400
    - 名称重复返回 409
    """
    try:
        channel = notify_service.update_channel(
            channel_id=channel_id,
            name=req.name,
            channel_type=req.type,
            config=req.config or {},
            enabled=req.enabled,
        )
        if not channel:
            raise HTTPException(status_code=404, detail=f"渠道不存在: {channel_id}")
        logger.info(f"通知渠道已更新，操作用户：{session['username']}，名称：{channel['name']}")
        return ApiResponse(
            data=NotifyChannelUpdateOut().model_dump()
        ).model_dump()
    except ValueError as e:
        msg = str(e)
        if "已存在" in msg:
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=400, detail=msg)


@router.delete("/{channel_id}", response_model=ApiResponse)
async def delete_channel(
    channel_id: str,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    删除通知渠道

    - 渠道不存在返回 404
    """
    deleted = notify_service.delete_channel(channel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"渠道不存在: {channel_id}")
    logger.info(f"通知渠道已删除，操作用户：{session['username']}，ID：{channel_id}")
    return ApiResponse(
        data=NotifyChannelDeleteOut().model_dump()
    ).model_dump()


# ==================== 测试发送 ====================


@router.post("/{channel_id}/test", response_model=ApiResponse)
async def test_channel(
    channel_id: str,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    测试通知渠道

    - 渠道不存在返回 404
    """
    channel = notify_service.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail=f"渠道不存在: {channel_id}")

    result = notify_service.test_channel(channel_id)
    if result["success"]:
        return ApiResponse(
            data=result,
            message="测试消息发送成功"
        ).model_dump()
    else:
        raise HTTPException(status_code=400, detail=result["message"])
