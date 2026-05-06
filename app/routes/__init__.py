"""
统一注册所有子路由
"""
from fastapi import APIRouter

from app.routes import (
    auth,
    cfst,
    hosts,
    trackers,
    clients,
    scheduler,
    settings,
    notify,
    backup,
    ikuai,
    mihosts,
    logs,
)

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["认证"])
router.include_router(cfst.router, prefix="/cfst", tags=["CFST"])
router.include_router(hosts.router, prefix="/hosts", tags=["Hosts"])
router.include_router(trackers.router, prefix="/trackers", tags=["Tracker"])
router.include_router(clients.router, prefix="/clients", tags=["下载器"])
router.include_router(scheduler.router, prefix="/scheduler", tags=["调度器"])
router.include_router(settings.router, prefix="/settings", tags=["设置"])
router.include_router(notify.router, prefix="/notify", tags=["通知"])
router.include_router(backup.router, prefix="/backup", tags=["备份"])
router.include_router(ikuai.router, prefix="/ikuai", tags=["爱快DNS"])
router.include_router(mihosts.router, prefix="/mihosts", tags=["小米路由器"])
router.include_router(logs.router, prefix="", tags=["日志"])
