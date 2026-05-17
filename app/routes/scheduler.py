"""
调度器路由：任务管理 / 启停 / 手动触发

API 列表：
    GET  /api/scheduler/status      - 获取调度器状态
    GET  /api/scheduler/jobs        - 获取任务列表
    POST /api/scheduler/jobs        - 添加/更新任务
    GET  /api/scheduler/jobs/{id}   - 获取单个任务
    DELETE /api/scheduler/jobs/{id} - 删除任务
    POST /api/scheduler/jobs/{id}/enable   - 启用任务
    POST /api/scheduler/jobs/{id}/disable  - 禁用任务
    POST /api/scheduler/jobs/{id}/run     - 手动触发任务
"""
from fastapi import APIRouter, Depends, HTTPException

from app.auth import verify_session, verify_csrf_token
from app.models import ApiResponse, SchedulerJobIn, SchedulerJobOut, SchedulerJobListOut
from app.services import scheduler_service
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/status", response_model=ApiResponse)
async def get_scheduler_status(session: dict = Depends(verify_session)):
    """
    获取调度器状态
    """
    jobs = scheduler_service.list_jobs()
    return ApiResponse(data={
        "running": scheduler_service.scheduler.running,
        "jobs": jobs,
    }).model_dump()


@router.get("/jobs", response_model=ApiResponse)
async def list_jobs(session: dict = Depends(verify_session)):
    """
    获取所有调度任务列表
    """
    jobs = scheduler_service.list_jobs()

    return ApiResponse(
        data=SchedulerJobListOut(jobs=jobs, total=len(jobs)).model_dump()
    ).model_dump()


@router.post("/jobs", response_model=ApiResponse)
async def create_job(
    req: SchedulerJobIn,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    添加或更新调度任务

    - job_id 存在时：更新配置
    - job_id 不存在时：创建新任务
    """
    try:
        job = scheduler_service.add_job(
            job_id=req.job_id,
            name=req.name,
            trigger=req.trigger,
            enabled=req.enabled,
            interval_seconds=req.interval_seconds or 3600,
            cron_expr=req.cron_expr,
        )
        logger.info(f"调度任务已创建或更新，操作用户：{session['username']}，任务 ID：{req.job_id}")
        return ApiResponse(data=job).model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/jobs/{job_id}", response_model=ApiResponse)
async def get_job(job_id: str, session: dict = Depends(verify_session)):
    """
    获取单个调度任务配置
    """
    job = scheduler_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"任务不存在: {job_id}")
    return ApiResponse(data=job).model_dump()


@router.delete("/jobs/{job_id}", response_model=ApiResponse)
async def delete_job(job_id: str, session: dict = Depends(verify_session), _csrf: None = Depends(verify_csrf_token)):
    """
    删除调度任务
    """
    success = scheduler_service.remove_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"任务不存在: {job_id}")

    logger.info(f"调度任务已删除，操作用户：{session['username']}，任务 ID：{job_id}")
    return ApiResponse(message="任务已删除").model_dump()


@router.post("/jobs/{job_id}/enable", response_model=ApiResponse)
async def enable_job(job_id: str, session: dict = Depends(verify_session), _csrf: None = Depends(verify_csrf_token)):
    """
    启用调度任务
    """
    job = scheduler_service.enable_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"任务不存在: {job_id}")

    logger.info(f"调度任务已启用，操作用户：{session['username']}，任务 ID：{job_id}")
    return ApiResponse(message="任务已启用", data=job).model_dump()


@router.post("/jobs/{job_id}/disable", response_model=ApiResponse)
async def disable_job(job_id: str, session: dict = Depends(verify_session), _csrf: None = Depends(verify_csrf_token)):
    """
    禁用调度任务（保留配置）
    """
    job = scheduler_service.disable_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"任务不存在: {job_id}")

    logger.info(f"调度任务已禁用，操作用户：{session['username']}，任务 ID：{job_id}")
    return ApiResponse(message="任务已禁用", data=job).model_dump()


@router.post("/jobs/{job_id}/run", response_model=ApiResponse)
async def run_job(job_id: str, session: dict = Depends(verify_session), _csrf: None = Depends(verify_csrf_token)):
    """
    手动触发任务执行（立即执行一次）
    """
    success = scheduler_service.trigger_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"任务不存在: {job_id}")

    logger.info(f"调度任务已手动触发，操作用户：{session['username']}，任务 ID：{job_id}")
    return ApiResponse(message="任务已触发").model_dump()
