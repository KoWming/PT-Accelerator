"""
小米路由器 Hosts 路由
"""
from fastapi import APIRouter

from app.config import config
from app.services.mihosts_service import MiHostsService
from app.services.cfst_service import cfst_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["小米路由器"])


def _get_service() -> MiHostsService | None:
    """从当前配置获取小米路由器服务实例"""
    if not config.get("mihosts.enabled", False):
        return None

    service = MiHostsService()
    service.init_config(
        app_id=config.get("mihosts.app_id", ""),
        device_id=config.get("mihosts.device_id", ""),
        client_id=config.get("mihosts.client_id", ""),
        scope=config.get("mihosts.scope", ""),
        token=config.get("mihosts.token", ""),
        ignore=config.get("mihosts.ignore", ""),
    )
    return service if service.is_enabled else None


@router.get("/status")
def get_status():
    """
    获取小米路由器配置状态
    """
    token = config.get("mihosts.token", "")
    return {
        "enabled": config.get("mihosts.enabled", False),
        "app_id": config.get("mihosts.app_id", ""),
        "device_id": config.get("mihosts.device_id", ""),
        "client_id": config.get("mihosts.client_id", ""),
        "scope": config.get("mihosts.scope", ""),
        "token": "********" if token else "",
        "ignore": config.get("mihosts.ignore", ""),
    }


@router.post("/test")
def test_connection(body: dict | None = None):
    """
    测试小米路由器连接
    """
    body = body or {}

    app_id = body.get("app_id") or config.get("mihosts.app_id", "")
    device_id = body.get("device_id") or config.get("mihosts.device_id", "")
    client_id = body.get("client_id") or config.get("mihosts.client_id", "")
    scope = body.get("scope") or config.get("mihosts.scope", "")
    token = body.get("token") or config.get("mihosts.token", "")
    ignore = body.get("ignore") or config.get("mihosts.ignore", "")

    enabled = body.get("enabled")
    if enabled is None:
        enabled = config.get("mihosts.enabled", False)

    if not enabled:
        return {"success": False, "message": "小米路由器同步未启用"}

    if not token:
        return {"success": False, "message": "请先填写 Token"}

    service = MiHostsService()
    service.init_config(
        app_id=app_id,
        device_id=device_id,
        client_id=client_id,
        scope=scope,
        token=token,
        ignore=ignore,
    )

    success, message = service.test_connection()
    return {"success": success, "message": message}


@router.get("/remote-hosts")
def get_remote_hosts():
    """
    获取小米路由器当前 hosts 内容
    """
    service = _get_service()

    if not service:
        return {"success": False, "message": "小米路由器同步未启用", "hosts": [], "count": 0}

    hosts, raw_text = service.get_remote_hosts()
    return {
        "success": True,
        "hosts": hosts,
        "raw_text": raw_text,
        "count": len(hosts),
    }


@router.post("/sync")
def sync_hosts():
    """
    将 CFST 缓存结果同步到小米路由器 hosts

    从 CFST 服务获取最新的 tracker URL → 最优 IP 映射，
    与远程 hosts 合并后写入小米路由器。
    """
    service = _get_service()

    if not service:
        return {"success": False, "message": "小米路由器同步未启用"}

    # 获取 CFST 缓存结果
    cf_ip_map: dict[str, str] = cfst_service.get_cached_results()
    if not cf_ip_map:
        return {"success": False, "message": "没有可用的 CFST 优选结果，请先运行 CFST 测速"}

    # 构建 cf_hosts 列表（tracker URL → hostname）
    from urllib.parse import urlparse

    cf_hosts: list[dict] = []
    for tracker_url, ip in cf_ip_map.items():
        try:
            parsed = urlparse(tracker_url)
            hostname = parsed.hostname if parsed.hostname else None
            if not hostname:
                import re

                m = re.match(r"^\w+://([^/:]+)", tracker_url)
                hostname = m.group(1) if m else None
            if hostname:
                cf_hosts.append({"domain": hostname, "ip": ip})
        except Exception:
            logger.warning(f"无法解析 tracker URL：{tracker_url}")
            continue

    if not cf_hosts:
        return {"success": False, "message": "CFST 结果中没有有效的 tracker 域名"}

    logger.info(f"准备同步 {len(cf_hosts)} 条 CFST 结果到小米路由器")
    success, message = service.sync_hosts(cf_hosts)

    if success:
        return {"success": True, "message": message, "cf_count": len(cf_hosts)}
    else:
        return {"success": False, "message": message}
