"""
备份路由：手动备份、恢复、WebDAV 配置
"""
from fastapi import APIRouter, Depends, HTTPException

from app.auth import verify_session, verify_csrf_token
from app.config import config
from app.utils.secret_crypto import decrypt_secret
from app.models import (
    ApiResponse,
    BackupConfigIn,
    BackupCreateIn,
    BackupCreateOut,
    BackupListOut,
    BackupRestoreOut,
    BackupDeleteOut,
    BackupTestIn,
    BackupTestOut,
)

from app.services.backup_service import backup_service
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


# ==================== 备份配置 ====================


@router.get("/config", response_model=ApiResponse)
async def get_backup_config(session_: dict = Depends(verify_session)):
    """
    获取备份配置
    """
    cfg = backup_service.get_config()
    return ApiResponse(data=cfg).model_dump()


@router.put("/config", response_model=ApiResponse)
async def update_backup_config(
    req: BackupConfigIn,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    更新备份配置

    - WebDAV URL 格式无效返回 400
    """
    try:
        # 只传递提供的字段
        update_kwargs = {}
        if req.webdav_enabled is not None:
            update_kwargs["webdav_enabled"] = req.webdav_enabled
        if req.webdav_url is not None:
            update_kwargs["webdav_url"] = req.webdav_url
        if req.webdav_username is not None:
            update_kwargs["webdav_username"] = req.webdav_username
        if req.webdav_password is not None:
            update_kwargs["webdav_password"] = req.webdav_password
        if req.webdav_path is not None:
            update_kwargs["webdav_path"] = req.webdav_path
        if req.local_keep_count is not None:
            update_kwargs["local_keep_count"] = req.local_keep_count

        backup_service.update_config(**update_kwargs)
        logger.info(f"备份配置已更新，操作用户：{session['username']}")
        return ApiResponse(message="备份配置已更新").model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/test", response_model=ApiResponse)
async def test_webdav_connection(
    req: BackupTestIn,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """测试 WebDAV 连接，不保存配置。"""
    current_cfg = backup_service._get_config()
    password = req.webdav_password
    if not password:
        # 从配置读取时需要解密
        password = decrypt_secret(current_cfg.get("webdav_password", ""))

    result = await backup_service.test_webdav_connection(
        webdav_url=req.webdav_url,
        webdav_username=req.webdav_username,
        webdav_password=password,
        webdav_path=req.webdav_path,
    )

    if result["success"]:
        logger.info(f"WebDAV 连接测试成功，操作用户：{session['username']}")
        return ApiResponse(data=BackupTestOut(**result).model_dump()).model_dump()

    raise HTTPException(status_code=400, detail=result["message"])



# ==================== 备份操作 ====================



@router.post("/run", response_model=ApiResponse)
async def run_backup(
    req: BackupCreateIn,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    手动触发备份
    """
    try:
        result = backup_service.create_backup(description=req.description)
        logger.info(f"手动备份已创建，操作用户：{session['username']}，备份 ID：{result['backup_id']}")

        # 检查是否启用 WebDAV，如启用则上传
        if config.get("backup.webdav_enabled") and config.get("backup.webdav_url"):
            upload_result = await backup_service.upload_to_webdav(result["backup_id"])
            if upload_result.get("success"):
                logger.info(f"WebDAV 上传成功，备份 ID：{result['backup_id']}")
            else:
                logger.warning(f"WebDAV 上传失败：{upload_result.get('message')}，备份 ID：{result['backup_id']}")

        return ApiResponse(
            data=BackupCreateOut(
                backup_id=result["backup_id"],
                message=result["message"],
            ).model_dump()
        ).model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history", response_model=ApiResponse)
async def get_history(session_: dict = Depends(verify_session)):
    """
    获取备份历史
    """
    backups = backup_service.list_backups()
    # 不返回 file_path（内部路径）
    for b in backups:
        b.pop("file_path", None)
    return ApiResponse(
        data=BackupListOut(
            backups=backups,
            total=len(backups),
        ).model_dump()
    ).model_dump()


@router.post("/{backup_id}/upload", response_model=ApiResponse)
async def upload_backup(
    backup_id: str,
    session_: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    上传备份到 WebDAV

    - 备份不存在返回 404
    """
    import asyncio

    # 检查备份是否存在
    backups = backup_service.list_backups()
    if not any(b.get("id") == backup_id for b in backups):
        raise HTTPException(status_code=404, detail=f"备份不存在: {backup_id}")

    # 异步上传
    result = await backup_service.upload_to_webdav(backup_id)

    if result["success"]:
        return ApiResponse(message=result["message"]).model_dump()
    else:
        raise HTTPException(status_code=400, detail=result["message"])


@router.post("/{backup_id}/restore", response_model=ApiResponse)
async def restore_backup(
    backup_id: str,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    从备份恢复

    - 备份不存在返回 404
    """
    import asyncio

    # 检查备份是否存在
    backups = backup_service.list_backups()
    if not any(b.get("id") == backup_id for b in backups):
        raise HTTPException(status_code=404, detail=f"备份不存在: {backup_id}")

    # 异步恢复
    result = await backup_service.restore_backup(backup_id)

    if result["success"]:
        logger.info(f"备份已恢复，操作用户：{session['username']}，备份 ID：{backup_id}")
        return ApiResponse(
            data=BackupRestoreOut().model_dump()
        ).model_dump()
    else:
        raise HTTPException(status_code=400, detail=result["message"])


@router.delete("/history/{backup_id}", response_model=ApiResponse)
async def delete_backup(
    backup_id: str,
    session_: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    删除备份

    - 备份不存在返回 404
    """
    deleted = await backup_service.delete_backup(backup_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"备份不存在: {backup_id}")
    logger.info(f"备份已删除，操作用户：{session_['username']}，备份 ID：{backup_id}")
    return ApiResponse(
        data=BackupDeleteOut().model_dump()
    ).model_dump()

