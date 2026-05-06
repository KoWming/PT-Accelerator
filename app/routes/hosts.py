"""
Hosts 路由：源管理、文件编辑、IP 查看
"""
import asyncio
import threading
import uuid

from fastapi import APIRouter, Depends, HTTPException


from app.auth import verify_session
from app.config import config


from app.models import (
    ApiResponse,
    HostsSourceIn,
    HostsSourceUpdateIn,
    HostsSourceCreateOut,
    HostsSourceUpdateOut,
    HostsSourceDeleteOut,
    HostsSourceListOut,
    HostsIpListOut,
    HostsUpdateOut,
)
from app.services.hosts_service import HostsService
from app.pipelines.hosts_pipeline import HostsPipeline
from app.utils.logger import get_logger


router = APIRouter()
logger = get_logger(__name__)

# 全局服务实例（延迟初始化）
_hosts_service: HostsService | None = None
_hosts_pipeline_lock = threading.Lock()
_hosts_pipeline_running = False
_hosts_pipeline_task_id: str | None = None


def get_hosts_service() -> HostsService:
    global _hosts_service
    if _hosts_service is None:
        _hosts_service = HostsService()
    return _hosts_service


def _get_hosts_pipeline_state() -> tuple[bool, str | None]:
    with _hosts_pipeline_lock:
        return _hosts_pipeline_running, _hosts_pipeline_task_id


def _set_hosts_pipeline_state(running: bool, task_id: str | None):
    global _hosts_pipeline_running, _hosts_pipeline_task_id
    with _hosts_pipeline_lock:
        _hosts_pipeline_running = running
        _hosts_pipeline_task_id = task_id


def _start_hosts_pipeline_background(task_id: str, force: bool, clear_first: bool, username: str):
    def _target():
        try:
            logger.info(
                f"Hosts 后台任务开始执行：task_id={task_id}，操作用户：{username}，"
                f"force={force}，clear_first={clear_first}"
            )
            asyncio.run(_run_hosts_pipeline(force=force, clear_first=clear_first))
            logger.info(f"Hosts 后台任务执行完成：task_id={task_id}")
        except Exception as e:
            logger.error(f"Hosts 后台任务执行失败：task_id={task_id}，错误：{e}", exc_info=True)
        finally:
            _set_hosts_pipeline_state(False, None)

    threading.Thread(target=_target, daemon=True, name=f"hosts-pipeline-{task_id}").start()


# ==================== Hosts 源 CRUD ====================


@router.get("/sources")
async def list_sources(session: dict = Depends(verify_session)):
    """列出所有 Hosts 源"""
    svc = get_hosts_service()
    sources = svc.list_sources()
    return ApiResponse(
        data=HostsSourceListOut(sources=sources, total=len(sources)).model_dump()
    ).model_dump()


@router.post("/sources", response_model_exclude_none=True)
async def add_source(
    body: HostsSourceIn,
    session: dict = Depends(verify_session),
):
    """新增 Hosts 源"""
    svc = get_hosts_service()
    try:
        new_source = svc.add_source(name=body.name, url=body.url, enabled=body.enabled)
        return ApiResponse(
            data=HostsSourceCreateOut(id=new_source["id"]).model_dump()
        ).model_dump()
    except ValueError as e:
        args = e.args
        if len(args) >= 2 and args[0] == "duplicate":
            raise HTTPException(status_code=409, detail=args[1])
        raise HTTPException(status_code=422, detail=str(e))


@router.put("/sources/{source_id}")
async def update_source(
    source_id: str,
    body: HostsSourceUpdateIn,
    session: dict = Depends(verify_session),
):
    """更新 Hosts 源"""
    svc = get_hosts_service()
    try:
        updated = svc.update_source(
            source_id=source_id,
            name=body.name,
            url=body.url,
            enabled=body.enabled,
        )
        if updated is None:
            raise HTTPException(status_code=404, detail=f"源不存在: {source_id}")
        return ApiResponse(
            data=HostsSourceUpdateOut().model_dump()
        ).model_dump()
    except ValueError as e:
        args = e.args
        if len(args) >= 2 and args[0] == "duplicate":
            raise HTTPException(status_code=409, detail=args[1])
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/sources/{source_id}")
async def get_source(
    source_id: str,
    session: dict = Depends(verify_session),
):
    """获取单个 Hosts 源"""
    svc = get_hosts_service()
    source = svc.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail=f"源不存在: {source_id}")
    return ApiResponse(data=source).model_dump()


@router.delete("/sources/{source_id}")
async def delete_source(
    source_id: str,
    session: dict = Depends(verify_session),
):
    """删除 Hosts 源"""
    svc = get_hosts_service()
    deleted = svc.delete_source(source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"源不存在: {source_id}")
    return ApiResponse(
        data=HostsSourceDeleteOut().model_dump()
    ).model_dump()


# ==================== IP 映射 & 内容 ====================


@router.get("/ips")
async def get_tracker_ips(session: dict = Depends(verify_session)):
    """查看当前 Hosts 文件中的 tracker IP 映射"""
    svc = get_hosts_service()
    ips = svc.get_current_ips()
    return ApiResponse(
        data=HostsIpListOut(ips=ips, total=len(ips)).model_dump()
    ).model_dump()


@router.get("/content")
async def get_content(session: dict = Depends(verify_session)):
    """获取当前 Hosts 文件内容"""
    svc = get_hosts_service()
    content = svc.get_hosts_content()
    return ApiResponse(data={"content": content}).model_dump()


@router.put("/content")
async def save_content(
    content: str,
    session: dict = Depends(verify_session),
):
    """直接写入 Hosts 文件内容"""
    svc = get_hosts_service()
    svc.write_hosts_content(content)
    logger.info(f"Hosts 内容已保存，操作用户：{session['username']}")
    return ApiResponse(message="Hosts 文件已保存").model_dump()


# ==================== 手动刷新 ====================


async def _run_hosts_pipeline(force: bool, clear_first: bool):
    from app.services.cfst_service import cfst_service

    svc = get_hosts_service()
    sources = svc.list_sources()

    if not sources:
        raise HTTPException(status_code=400, detail="未配置任何 hosts 源")

    cf_ip_map = cfst_service.get_cached_results()
    if not cf_ip_map and not force:
        raise HTTPException(
            status_code=400,
            detail="无可用的 CFST IP 数据，请先运行测速 (/api/cfst/run)"
        )

    pipeline = HostsPipeline()
    try:
        result = await pipeline.run(sources=sources, cf_ip_map=cf_ip_map, clear_first=clear_first)
        if not result["success"]:
            raise HTTPException(status_code=500, detail="; ".join(result["errors"]))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hosts refresh failed: {e}")
        raise HTTPException(status_code=500, detail=f"刷新失败: {e}")


@router.post("/refresh")
async def refresh_hosts(
    force: bool = False,
    session: dict = Depends(verify_session),
):
    """
    手动刷新 Hosts
    流程：1. 从 CFST 结果获取 IP 映射 → 2. 拉取所有源 → 3. 合并写入
    """
    running, running_task_id = _get_hosts_pipeline_state()
    if running:
        raise HTTPException(status_code=409, detail=f"Hosts 任务正在进行中（task_id={running_task_id}），请稍后再试")

    task_id = uuid.uuid4().hex[:8]
    _set_hosts_pipeline_state(True, task_id)
    _start_hosts_pipeline_background(task_id, force=force, clear_first=False, username=session["username"])

    return ApiResponse(
        data=HostsUpdateOut(message="Hosts 刷新后台任务已启动", task_id=task_id).model_dump()
    ).model_dump()


@router.post("/rebuild")
async def rebuild_hosts(
    force: bool = True,
    session: dict = Depends(verify_session),
):
    """先清空项目写入分区，再重新执行 Hosts 生成流程。"""
    running, running_task_id = _get_hosts_pipeline_state()
    if running:
        raise HTTPException(status_code=409, detail=f"Hosts 任务正在进行中（task_id={running_task_id}），请稍后再试")

    task_id = uuid.uuid4().hex[:8]
    _set_hosts_pipeline_state(True, task_id)
    _start_hosts_pipeline_background(task_id, force=force, clear_first=True, username=session["username"])

    return ApiResponse(
        data=HostsUpdateOut(message="Hosts 清空重建后台任务已启动", task_id=task_id).model_dump()
    ).model_dump()


# ==================== Hosts 配置 ====================



@router.get("/config")
async def get_hosts_config(session: dict = Depends(verify_session)):
    """获取 Hosts 配置"""
    return ApiResponse(data={
        "target_path": config.get("hosts.target_path", default=""),
        "backup_enabled": config.get("hosts.backup_enabled", default=True),
    }).model_dump()


@router.put("/config")
async def update_hosts_config(
    target_path: str | None = None,
    backup_enabled: bool | None = None,
    session: dict = Depends(verify_session),
):
    """更新 Hosts 配置"""
    if target_path is not None:
        config.set("hosts.target_path", target_path)
    if backup_enabled is not None:
        config.set("hosts.backup_enabled", backup_enabled)
    config.save()
    return ApiResponse(data={"message": "Hosts 配置已更新"}).model_dump()
