"""
CFST 路由：触发测速、状态查询、参数配置

API 列表：
    POST /api/cfst/run      - 手动触发测速
    GET  /api/cfst/status   - 查询测速状态
    GET  /api/cfst/results  - 获取测速结果
    GET  /api/cfst/config   - 获取 CFST 参数配置
    PUT  /api/cfst/config   - 更新 CFST 参数配置
"""
from fastapi import APIRouter, Depends, HTTPException

from app.auth import verify_session
from app.config import config
from app.models import (

    ApiResponse,
    CfstConfigIn,
    CfstConfigOut,
    CfstRunIn,
    CfstRunOut,
    CfstStatusOut,
    CfstResultsOut,
)
from app.pipelines.cfst_pipeline import CfstPipeline
from app.services.cfst_service import cfst_service
from app.services.tracker_service import tracker_service
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/run", response_model=ApiResponse)
async def run_cfst(
    body: CfstRunIn,
    session: dict = Depends(verify_session),
):
    """手动触发 CloudflareSpeedTest。"""
    _ = body

    if cfst_service.running:
        raise HTTPException(
            status_code=409,
            detail=f"测速正在进行中（task_id={cfst_service.task_id}），请等待完成后重试",
        )

    cloudflare_trackers = tracker_service.list_enabled_cloudflare()
    if not cloudflare_trackers:
        raise HTTPException(status_code=400, detail="当前没有已启用的 Cloudflare Tracker，无法执行优选")

    trackers = [tracker.get("url", "") for tracker in cloudflare_trackers if tracker.get("url")]
    pipeline = CfstPipeline()
    task_id = pipeline.run_in_background(trackers=trackers)

    logger.info(
        f"CFST 已由 {session['username']} 手动提交后台执行，task_id={task_id}，"
        f"Cloudflare Tracker 数量={len(cloudflare_trackers)}"
    )

    return ApiResponse(
        data=CfstRunOut(
            task_id=task_id,
            message="Cloudflare IP 优选后台任务已启动",
        ).model_dump()
    ).model_dump()



@router.get("/status", response_model=ApiResponse)
async def get_status(session: dict = Depends(verify_session)):
    """查询当前测速状态。"""
    _ = session
    status = cfst_service.get_status()

    return ApiResponse(
        data=CfstStatusOut(
            running=status["running"],
            task_id=status["task_id"],
            progress=status["progress"],
            result_count=status["result_count"],
            message=status["message"],
            started_at=status["started_at"],
        ).model_dump()
    ).model_dump()



@router.get("/results", response_model=ApiResponse)
async def get_results(session: dict = Depends(verify_session)):
    """获取最新测速结果。"""
    _ = session
    results = cfst_service.get_results()
    result_file = str(cfst_service.csv_results_file) if cfst_service.csv_results_file.exists() else None

    best_ip = None
    for item in results:
        if item.get("ip"):
            best_ip = item["ip"]
            break

    return ApiResponse(
        data=CfstResultsOut(
            results=results,
            total=len(results),
            best_ip=best_ip,
            result_file=result_file,
        ).model_dump()
    ).model_dump()



@router.get("/config", response_model=ApiResponse)
async def get_cfst_config(session: dict = Depends(verify_session)):
    """获取 CFST 参数配置。"""
    _ = session
    runtime_config = cfst_service.get_runtime_config()

    return ApiResponse(
        data=CfstConfigOut(
            **runtime_config,
            binary_path=config.get("cfst.binary_path") or None,
        ).model_dump()
    ).model_dump()


@router.put("/config", response_model=ApiResponse)
async def update_cfst_config(
    req: CfstConfigIn,
    session: dict = Depends(verify_session),
):
    """更新 CFST 参数配置。"""
    if req.min_delay > req.max_delay:
        raise HTTPException(status_code=400, detail="平均延迟下限不能大于平均延迟上限")

    config.set("cfst.threads", req.threads)
    config.set("cfst.ping_times", req.ping_times)
    config.set("cfst.download_count", req.download_count)
    config.set("cfst.download_time", req.download_time)
    config.set("cfst.timeout_seconds", req.timeout_seconds)


    config.set("cfst.tcp_port", req.tcp_port)
    config.set("cfst.url", req.url)
    config.set("cfst.httping", req.httping)
    config.set("cfst.httping_code", req.httping_code)
    config.set("cfst.cfcolo", req.cfcolo)
    config.set("cfst.min_delay", req.min_delay)
    config.set("cfst.max_delay", req.max_delay)
    config.set("cfst.max_loss_rate", req.max_loss_rate)
    config.set("cfst.min_speed", req.min_speed)
    config.set("cfst.show_count", req.show_count)
    config.set("cfst.test_all", req.test_all)
    config.set("cfst.disable_download", req.disable_download)
    config.set("cfst.debug", req.debug)
    config.set("cfst.additional_args", req.additional_args)
    config.save()

    logger.info(
        "CFST 配置已更新，操作用户：%s，threads=%s，download_count=%s，httping=%s",
        session["username"],
        req.threads,
        req.download_count,
        req.httping,
    )
    return ApiResponse(message="CFST 配置已更新").model_dump()

