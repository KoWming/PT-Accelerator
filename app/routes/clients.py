"""
下载器路由：qBittorrent / Transmission 管理
"""
import threading
import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.auth import verify_session
from app.models import (
    ApiResponse,
    DownloaderIn,
    DownloaderOut,
    DownloaderListOut,
    DownloaderAddOut,
    DownloaderDeleteOut,
    DownloaderTestIn,
    TrackerBatchImportOut,
    TrackerImportTaskOut,
)

from app.services.clients_service import clients_service
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
_clients_import_lock = threading.Lock()
_clients_import_running = False
_clients_import_task_id: str | None = None


def _get_clients_import_state() -> tuple[bool, str | None]:
    with _clients_import_lock:
        return _clients_import_running, _clients_import_task_id


def _set_clients_import_state(running: bool, task_id: str | None):
    global _clients_import_running, _clients_import_task_id
    with _clients_import_lock:
        _clients_import_running = running
        _clients_import_task_id = task_id


def _start_import_trackers_background(task_id: str, username: str):
    def _target():
        try:
            logger.info(f"下载器导入 Tracker 后台任务开始执行：task_id={task_id}，操作用户：{username}")
            result = clients_service.import_trackers_from_clients()
            logger.info(
                f"下载器导入 Tracker 后台任务执行完成：task_id={task_id}，"
                f"新增 {result.get('imported', 0)}，跳过 {result.get('skipped', 0)}"
            )
        except Exception as e:
            logger.error(f"下载器导入 Tracker 后台任务执行失败：task_id={task_id}，错误：{e}", exc_info=True)
        finally:
            _set_clients_import_state(False, None)

    threading.Thread(target=_target, daemon=True, name=f"clients-import-trackers-{task_id}").start()


# ==================== 客户端 CRUD ====================


@router.get("/", response_model=ApiResponse)
async def list_clients(session: dict = Depends(verify_session)):
    """
    列出所有下载器客户端
    """
    clients = clients_service.list_clients()
    return ApiResponse(
        data=DownloaderListOut(
            downloaders=clients,
            total=len(clients),
        ).model_dump()
    ).model_dump()


@router.get("/types", response_model=ApiResponse)
async def get_client_types(session: dict = Depends(verify_session)):
    """
    获取支持的客户端类型
    """
    types = clients_service.get_supported_types()
    return ApiResponse(data={"types": types}).model_dump()


@router.post("/", response_model=ApiResponse)
async def add_client(
    req: DownloaderIn,
    session: dict = Depends(verify_session),
):
    """
    添加新的下载器客户端

    - 类型无效返回 400
    - 主机格式无效返回 400
    - 端口无效返回 400
    - 重复客户端返回 409
    """
    try:
        client = clients_service.add_client(
            name=req.name,
            client_type=req.type,
            host=req.host,
            port=req.port,
            username=req.username or "",
            password=req.password or "",
            enabled=req.enabled,
            version=req.version,
        )
        logger.info(f"下载器已添加，操作用户：{session['username']}，名称：{client['name']}")
        return ApiResponse(
            data=DownloaderAddOut(id=client["id"]).model_dump()
        ).model_dump()
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg or "已存在" in msg:
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=400, detail=msg)


@router.post("/import-trackers", response_model=ApiResponse)
async def import_trackers(session: dict = Depends(verify_session)):
    """
    从所有已启用下载器导入 Tracker 到当前 Tracker 列表
    """
    running, running_task_id = _get_clients_import_state()
    if running:
        raise HTTPException(status_code=409, detail=f"导入任务正在进行中（task_id={running_task_id}），请稍后再试")

    task_id = uuid.uuid4().hex[:8]
    _set_clients_import_state(True, task_id)
    _start_import_trackers_background(task_id, session["username"])

    logger.info(f"下载器导入 Tracker 请求已提交后台执行，操作用户：{session['username']}，task_id={task_id}")
    return ApiResponse(data=TrackerImportTaskOut(task_id=task_id).model_dump()).model_dump()



@router.get("/{client_id}", response_model=ApiResponse)
async def get_client(client_id: str, session: dict = Depends(verify_session)):

    """
    获取单个下载器客户端
    """
    client = clients_service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail=f"客户端不存在: {client_id}")
    return ApiResponse(data=client).model_dump()


@router.put("/{client_id}", response_model=ApiResponse)
async def update_client(
    client_id: str,
    req: DownloaderIn,
    session: dict = Depends(verify_session),
):
    """
    更新下载器客户端

    - 客户端不存在返回 404
    - 主机格式无效返回 400
    - 端口无效返回 400
    - 重复客户端返回 409
    """
    try:
        client = clients_service.update_client(
            client_id=client_id,
            name=req.name,
            host=req.host,
            port=req.port,
            username=req.username or "",
            password=req.password or "",
            enabled=req.enabled,
            version=req.version,
        )
        if not client:
            raise HTTPException(status_code=404, detail=f"客户端不存在: {client_id}")
        logger.info(f"下载器已更新，操作用户：{session['username']}，名称：{client['name']}")
        return ApiResponse(data={"message": "下载器已更新"}).model_dump()
    except ValueError as e:
        msg = str(e)
        if "已存在" in msg:
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=400, detail=msg)


@router.delete("/{client_id}", response_model=ApiResponse)
async def delete_client(
    client_id: str,
    session: dict = Depends(verify_session),
):
    """
    删除下载器客户端

    - 客户端不存在返回 404
    """
    deleted = clients_service.delete_client(client_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"客户端不存在: {client_id}")
    logger.info(f"下载器已删除，操作用户：{session['username']}，ID：{client_id}")
    return ApiResponse(
        data=DownloaderDeleteOut().model_dump()
    ).model_dump()


# ==================== 连接测试 ====================


@router.post("/{client_id}/test", response_model=ApiResponse)
async def test_client(
    client_id: str,
    session: dict = Depends(verify_session),
):
    """
    测试下载器连接（已保存的客户端）

    - 客户端不存在返回 404
    """
    # 先检查客户端是否存在
    client = clients_service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail=f"客户端不存在: {client_id}")

    result = clients_service.test_connection(client_id)
    return ApiResponse(data=result).model_dump()


@router.post("/test", response_model=ApiResponse)
async def test_client_by_config(
    req: DownloaderTestIn,
    session: dict = Depends(verify_session),
):
    """
    测试下载器连接（临时配置，不保存）

    - 类型无效返回 400
    """
    if req.type not in ["qbittorrent", "transmission"]:
        raise HTTPException(status_code=400, detail=f"不支持的客户端类型: {req.type}")

    result = clients_service.test_connection_by_config(
        client_type=req.type,
        host=req.host,
        port=req.port,
        username=req.username or "",
        password=req.password or "",
    )
    return ApiResponse(data=result).model_dump()
