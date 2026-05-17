"""
Tracker 路由：CRUD、批量导入

API 列表：
    GET    /api/trackers/           - 列出所有 tracker
    POST   /api/trackers/           - 新增单个 tracker
    GET    /api/trackers/{id}       - 获取单个 tracker
    PUT    /api/trackers/{id}       - 更新 tracker
    DELETE /api/trackers/{id}       - 删除 tracker
    POST   /api/trackers/batch      - 批量导入 tracker
    GET    /api/trackers/enabled    - 仅列出已启用的 tracker（供 CFST 使用）
"""
from fastapi import APIRouter, Depends, HTTPException

from app.auth import verify_session, verify_csrf_token
from app.models import (
    ApiResponse,
    TrackerIn,
    TrackerOut,
    TrackerListOut,
    TrackerCreateOut,
    TrackerUpdateOut,
    TrackerDeleteOut,
    TrackerClearOut,
    TrackerBatchUpdateIpIn,
    TrackerBatchUpdateIpOut,
    TrackerBatchImportIn,
    TrackerBatchImportOut,
    TrackerCloudflareDomainsIn,
    TrackerCloudflareDomainsOut,
)




from app.services.cloudflare_detector import cloudflare_detector
from app.services.tracker_service import tracker_service
from app.services.tracker_store import tracker_store

from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


TRACKER_PUBLIC_FIELDS = ("id", "name", "url", "enabled", "ip")


def _normalize_cloudflare_domains(domains: list[str] | tuple[str, ...] | set[str]) -> list[str]:
    normalized: list[str] = []
    for domain in domains:
        normalized_domain = cloudflare_detector._normalize_domain(domain or "")
        if normalized_domain and normalized_domain not in normalized:
            normalized.append(normalized_domain)
    return sorted(normalized)


def _get_cloudflare_domains() -> list[str]:
    return _normalize_cloudflare_domains(tracker_store.load_cloudflare_domains())


def _serialize_tracker(tracker: dict) -> dict:

    return {
        field: tracker.get(field)
        for field in TRACKER_PUBLIC_FIELDS
        if field in tracker
    }


@router.get("/", response_model=ApiResponse)
async def list_trackers(session: dict = Depends(verify_session)):

    """
    列出所有 tracker
    """
    trackers = [_serialize_tracker(item) for item in tracker_service.list_trackers()]
    return ApiResponse(
        data=TrackerListOut(
            trackers=trackers,
            total=len(trackers),
        ).model_dump()
    ).model_dump()



@router.get("/enabled", response_model=ApiResponse)
async def list_enabled_trackers(session: dict = Depends(verify_session)):
    """
    仅列出已启用且判定为 Cloudflare 的 tracker（供 CFST Pipeline 使用）
    """
    trackers = [_serialize_tracker(item) for item in tracker_service.list_enabled_cloudflare()]
    return ApiResponse(
        data={
            "trackers": trackers,
            "total": len(trackers),
        }
    ).model_dump()




@router.get("/cloudflare-domains", response_model=ApiResponse)
async def list_cloudflare_domains(session: dict = Depends(verify_session)):
    """
    列出 Cloudflare 域名名单
    """
    domains = _get_cloudflare_domains()
    return ApiResponse(
        data=TrackerCloudflareDomainsOut(
            domains=domains,
            total=len(domains),
        ).model_dump()
    ).model_dump()


@router.put("/cloudflare-domains", response_model=ApiResponse)
async def update_cloudflare_domains(
    req: TrackerCloudflareDomainsIn,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    更新 Cloudflare 域名名单
    """
    domains = _normalize_cloudflare_domains(req.domains)
    tracker_store.save_cloudflare_domains(domains)
    tracker_service.sync_cloudflare_flags()
    logger.info(f"Cloudflare 域名名单已更新，操作用户：{session['username']}，数量：{len(domains)}")
    return ApiResponse(
        data=TrackerCloudflareDomainsOut(
            domains=domains,
            total=len(domains),
        ).model_dump(),
        message="Cloudflare 域名名单已更新",
    ).model_dump()


@router.put("/ip", response_model=ApiResponse)
async def batch_update_trackers_ip(

    req: TrackerBatchUpdateIpIn,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    批量更新全部 tracker 的当前 IP
    """
    try:
        updated = tracker_service.update_all_trackers_ip(req.ip)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    logger.info(f"Tracker 当前 IP 已批量更新，操作用户：{session['username']}，数量：{updated}，IP：{req.ip}")
    return ApiResponse(
        data=TrackerBatchUpdateIpOut(
            updated=updated,
            ip=req.ip,
            message=f"已将 {updated} 条 Tracker 的当前 IP 更新为 {req.ip}" if updated else "当前没有可更新的 Tracker",
        ).model_dump()
    ).model_dump()


@router.get("/{tracker_id}", response_model=ApiResponse)
async def get_tracker(tracker_id: str, session: dict = Depends(verify_session)):
    """
    获取单个 tracker
    """
    tracker = tracker_service.get_tracker(tracker_id)
    if not tracker:
        raise HTTPException(status_code=404, detail=f"Tracker 不存在: {tracker_id}")
    return ApiResponse(data=_serialize_tracker(tracker)).model_dump()



@router.post("/", response_model=ApiResponse)
async def add_tracker(
    req: TrackerIn,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    新增单个 tracker

    - URL 格式不正确返回 400
    - URL 已存在返回 409
    """
    try:
        tracker = tracker_service.add_tracker(
            name=req.name,
            url=req.url,
            enabled=req.enabled,
        )
        logger.info(f"Tracker 已创建，操作用户：{session['username']}，名称：{tracker['name']}，ID：{tracker['id']}")
        return ApiResponse(
            data=TrackerCreateOut(
                id=tracker["id"],
                message="Tracker 已创建",
            ).model_dump()
        ).model_dump()
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg or "已存在" in msg:
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=400, detail=msg)


@router.put("/{tracker_id}", response_model=ApiResponse)
async def update_tracker(
    tracker_id: str,
    req: TrackerIn,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    更新 tracker

    - tracker 不存在返回 404
    - 新 URL 格式不正确返回 400
    - 新 URL 与其他 tracker 冲突返回 409
    """
    try:
        tracker = tracker_service.update_tracker(
            tracker_id=tracker_id,
            name=req.name,
            url=req.url,
            enabled=req.enabled,
        )
        if not tracker:
            raise HTTPException(status_code=404, detail=f"Tracker 不存在: {tracker_id}")
        logger.info(f"Tracker 已更新，操作用户：{session['username']}，名称：{tracker['name']}，ID：{tracker['id']}")
        return ApiResponse(
            data=TrackerUpdateOut(message="Tracker 已更新").model_dump()
        ).model_dump()
    except ValueError as e:
        msg = str(e)
        if "already used" in msg or "已被使用" in msg:
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=400, detail=msg)


@router.delete("/{tracker_id}", response_model=ApiResponse)
async def delete_tracker(
    tracker_id: str,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    删除 tracker

    - tracker 不存在返回 404（但仍然返回成功）
    """
    deleted = tracker_service.delete_tracker(tracker_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Tracker 不存在: {tracker_id}")
    logger.info(f"Tracker 已删除，操作用户：{session['username']}，ID：{tracker_id}")
    return ApiResponse(
        data=TrackerDeleteOut(message="Tracker 已删除").model_dump()
    ).model_dump()


@router.delete("/", response_model=ApiResponse)


async def clear_all_trackers(session: dict = Depends(verify_session), _csrf: None = Depends(verify_csrf_token)):
    """
    清空全部 tracker
    """
    cleared = tracker_service.clear_all_trackers()
    logger.info(f"Tracker 已清空，操作用户：{session['username']}，数量：{cleared}")
    return ApiResponse(
        data=TrackerClearOut(
            cleared=cleared,
            message="Tracker 已清空" if cleared else "当前没有可清空的 Tracker",
        ).model_dump()
    ).model_dump()


@router.post("/batch", response_model=ApiResponse)

async def batch_import_trackers(
    req: TrackerBatchImportIn,
    session: dict = Depends(verify_session),
    _csrf: None = Depends(verify_csrf_token),
):
    """
    批量导入 tracker

    支持格式：
    - 逗号分隔：udp://a.com, udp://b.com
    - 换行分隔：每行一个 URL
    - 混合格式

    返回导入成功数量和跳过数量（重复或格式无效）
    """
    imported, skipped, imported_items = tracker_service.batch_import(
        urls=req.urls,
        enabled=req.enabled,
    )
    cloudflare_domains = sorted([
        item["url"] for item in imported_items if item.get("is_cloudflare")
    ])
    non_cloudflare_domains = sorted([
        item["url"] for item in imported_items if not item.get("is_cloudflare")
    ])
    logger.info(
        f"批量导入 Tracker，操作用户：{session['username']}，"
        f"成功：{imported}，跳过：{skipped}，"
        f"Cloudflare：{len(cloudflare_domains)}，非 Cloudflare：{len(non_cloudflare_domains)}"
    )
    return ApiResponse(
        data=TrackerBatchImportOut(
            imported=imported,
            skipped=skipped,
            cloudflare_domains=cloudflare_domains,
            non_cloudflare_domains=non_cloudflare_domains,
            message=f"批量导入完成：{imported} 个成功，{skipped} 个跳过",
        ).model_dump()
    ).model_dump()

