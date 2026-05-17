"""
爱快 DNS 路由
"""
from fastapi import APIRouter, Response, Depends
from typing import Any
from urllib.parse import urlparse

from app.auth import verify_session, verify_csrf_token
from app.config import config
from app.services.ikuai_service import IkuaiService
from app.utils.secret_crypto import encrypt_secret, decrypt_secret

router = APIRouter(tags=["爱快DNS"])


def _remove_config_key(data: dict[str, Any], key: str) -> None:
    """删除点号路径配置键。"""
    keys = key.split(".")
    target = data
    for item in keys[:-1]:
        value = target.get(item)
        if not isinstance(value, dict):
            return
        target = value
    target.pop(keys[-1], None)


def _normalize_ikuai_endpoint(host: str, port: int | None = None) -> tuple[str, int, str]:
    """规范化爱快地址；协议和非默认端口直接保留在 host 字段中。"""
    raw_host = str(host or "").strip().rstrip("/")
    if not raw_host:
        return "", port or 80, ""

    parsed = urlparse(raw_host if "://" in raw_host else f"http://{raw_host}")
    use_https = parsed.scheme.lower() == "https"
    hostname = parsed.hostname or raw_host
    normalized_port = port or parsed.port or (443 if use_https else 80)
    scheme = "https" if use_https else "http"
    is_default_port = (use_https and normalized_port == 443) or (not use_https and normalized_port == 80)
    normalized_host = f"{scheme}://{hostname}{'' if is_default_port else f':{normalized_port}'}"
    return normalized_host, normalized_port, scheme


def _get_ikuai_service() -> IkuaiService | None:
    """获取爱快服务实例（如果已启用）"""
    if not config.get("ikuai.enabled", False):
        return None

    service = IkuaiService()
    service.init_config(
        host=config.get("ikuai.host", ""),
        port=None,
        username=config.get("ikuai.username", "admin"),
        password=decrypt_secret(config.get("ikuai.password", "")),
    )
    return service


@router.get("/status")
def get_status(session: dict = Depends(verify_session)):
    """
    获取爱快 DNS 配置状态
    """
    enabled = config.get("ikuai.enabled", False)
    host = config.get("ikuai.host", "")
    password = config.get("ikuai.password", "")

    return {
        "enabled": enabled,
        "host": host,
        "username": config.get("ikuai.username", "admin"),
        # 密码脱敏返回，有值时显示 ********
        "password": "********" if password else "",
    }


@router.post("/test")
def test_connection(body: dict | None = None, session: dict = Depends(verify_session), _csrf: None = Depends(verify_csrf_token)):
    """
    测试爱快路由器连接
    """
    body = body or {}

    host = body.get("host", "") or config.get("ikuai.host", "")
    username = body.get("username", "admin") or config.get("ikuai.username", "admin")
    # 若 body 中没有传入新密码，从配置中读取并解密
    password = body.get("password", "") or decrypt_secret(config.get("ikuai.password", ""))
    port = body.get("port")
    if port is None:
        port = None

    host, port, _scheme = _normalize_ikuai_endpoint(host, port)

    enabled = body.get("enabled")
    if enabled is None:
        enabled = config.get("ikuai.enabled", False)

    if not enabled:
        return {"success": False, "message": "爱快 DNS 功能未启用"}

    if not host:
        return {"success": False, "message": "请先填写爱快路由器地址"}

    if not password:
        return {"success": False, "message": "请先填写爱快密码"}

    service = IkuaiService()
    service.init_config(
        host=host,
        port=port,
        username=username,
        password=password,
    )

    success, message = service.test_connection()
    service.close()

    return {"success": success, "message": message}



@router.get("/records")
def get_records(session: dict = Depends(verify_session)):
    """
    获取爱快 DNS 记录列表
    """
    service = _get_ikuai_service()

    if not service:
        return {"success": False, "message": "爱快 DNS 功能未启用", "records": []}

    records = service.get_dns_records()
    service.close()

    return {"success": True, "records": records}


@router.post("/sync")
def sync_dns(hosts: list[dict], session: dict = Depends(verify_session), _csrf: None = Depends(verify_csrf_token)):
    """
    同步 hosts 到爱快 DNS

    Args:
        hosts: [{"domain": "example.com", "ip": "1.2.3.4"}, ...]
    """
    service = _get_ikuai_service()

    if not service:
        return {"success": False, "message": "爱快 DNS 功能未启用"}

    if not hosts:
        return {"success": False, "message": "没有需要同步的 hosts"}

    success = service.sync_hosts_to_dns(hosts)
    service.close()

    if success:
        return {"success": True, "message": f"成功同步 {len(hosts)} 条记录"}
    else:
        return {"success": False, "message": "同步失败，请检查爱快路由器连接"}


@router.post("/sync-now")
def sync_now(session: dict = Depends(verify_session), _csrf: None = Depends(verify_csrf_token)):
    """
    手动立即同步：读取当前 CFST 最优 IP，将 Cloudflare Tracker 记录写入爱快 DNS。
    不需要重新跑 CFST，直接复用上次的缓存结果。
    """
    if not config.get("ikuai.enabled", False):
        return {"success": False, "message": "爱快 DNS 功能未启用"}

    # 拿 CFST 缓存结果（tracker URL → 当前最优 IP）
    from app.services.cfst_service import cfst_service
    cf_ip_map = cfst_service.get_cached_results()
    if not cf_ip_map:
        return {"success": False, "message": "暂无 CFST 优选结果，请先执行一次 IP 优选"}

    # 把 tracker URL 转为 {domain, ip} 列表
    from urllib.parse import urlparse as _urlparse
    import re as _re

    def _tracker_to_hostname(tracker_url: str) -> str | None:
        try:
            parsed = _urlparse(tracker_url)
            if parsed.hostname:
                return parsed.hostname
            m = _re.match(r"^\w+://([^/:]+)", tracker_url)
            return m.group(1) if m else None
        except Exception:
            return None

    cf_hosts = []
    for tracker_url, ip in cf_ip_map.items():
        hostname = _tracker_to_hostname(tracker_url)
        if hostname:
            cf_hosts.append({"domain": hostname, "ip": ip})

    if not cf_hosts:
        return {"success": False, "message": "没有可同步的 Cloudflare Tracker 域名"}

    service = _get_ikuai_service()
    if not service:
        return {"success": False, "message": "爱快 DNS 未启用或配置不完整"}

    try:
        success = service.sync_hosts_to_dns(cf_hosts)
        service.close()
        if success:
            return {
                "success": True,
                "message": f"同步完成，共写入 {len(cf_hosts)} 条 Tracker 域名",
                "synced_count": len(cf_hosts),
                "records": cf_hosts,
            }
        else:
            return {"success": False, "message": "同步失败，请检查爱快路由器连接"}
    except Exception as e:
        return {"success": False, "message": f"同步出错：{e}"}


@router.post("/save")
def save_config(body: dict, session: dict = Depends(verify_session), _csrf: None = Depends(verify_csrf_token)):
    """
    保存爱快 DNS 配置

    Args:
        body: {"enabled": bool, "host": str, "port": int, "username": str, "password": str}
    """
    enabled = body.get("enabled", False)
    host = body.get("host", "")
    port = body.get("port")
    username = body.get("username", "admin")
    password = body.get("password", "")

    host, port, _scheme = _normalize_ikuai_endpoint(host, port)

    # 保存到配置
    config.set("ikuai.enabled", enabled)
    config.set("ikuai.host", host)
    config.set("ikuai.username", username)
    _remove_config_key(config._data, "ikuai.port")
    _remove_config_key(config._data, "ikuai.use_https")

    # 只有密码不为空时才更新，写入前加密
    if password:
        config.set("ikuai.password", encrypt_secret(password))

    config.save()

    # 如果启用了配置，测试连接
    if enabled and host and password:
        service = IkuaiService()
        service.init_config(host=host, port=port, username=username, password=password)
        success, message = service.test_connection()
        service.close()

        if success:
            return {"success": True, "message": "配置已保存，连接测试成功"}
        else:
            return {"success": False, "message": f"配置已保存，但连接测试失败：{message}"}

    return {"success": True, "message": "配置已保存"}


@router.post("/export-dns")
def export_dns(session: dict = Depends(verify_session), _csrf: None = Depends(verify_csrf_token)):
    """
    导出爱快 DNS 配置为 TXT 文件并返回文件内容。
    """
    service = _get_ikuai_service()
    if not service:
        return {"success": False, "message": "爱快 DNS 功能未启用"}

    content = service.export_dns_txt()
    service.close()

    if content is None:
        return {"success": False, "message": "导出失败，请检查爱快路由器连接"}

    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="ikuai_dns.txt"'},
    )


@router.post("/import-dns")
async def import_dns(body: dict, session: dict = Depends(verify_session), _csrf: None = Depends(verify_csrf_token)):
    """
    从 Base64 编码的 TXT 文件内容导入 DNS 记录。

    Args:
        body: {"content": "<base64 string>", "append": bool}
    """
    import base64

    service = _get_ikuai_service()
    if not service:
        return {"success": False, "message": "爱快 DNS 功能未启用"}

    b64_content = body.get("content", "")
    append = bool(body.get("append", False))

    if not b64_content:
        return {"success": False, "message": "缺少文件内容（content 字段）"}

    try:
        file_bytes = base64.b64decode(b64_content)
    except Exception:
        return {"success": False, "message": "文件内容 Base64 解码失败，请确认格式正确"}

    success = service.import_dns_txt(file_bytes, append=append)
    service.close()

    mode = "追加" if append else "覆盖"
    if success:
        return {"success": True, "message": f"DNS 配置导入成功（{mode}模式）"}
    else:
        return {"success": False, "message": f"DNS 配置导入失败（{mode}模式），请检查文件格式或爱快连接"}


@router.post("/delete-record")
def delete_record(body: dict, session: dict = Depends(verify_session), _csrf: None = Depends(verify_csrf_token)):
    """
    删除指定 DNS 记录。

    Args:
        body: {"id": str|int}
    """
    service = _get_ikuai_service()
    if not service:
        return {"success": False, "message": "爱快 DNS 功能未启用"}

    record_id = body.get("id")
    if record_id is None:
        return {"success": False, "message": "缺少记录 ID（id 字段）"}

    success = service.delete_dns_record(record_id)
    service.close()

    if success:
        return {"success": True, "message": f"DNS 记录已删除（ID={record_id}）"}
    else:
        return {"success": False, "message": "DNS 记录删除失败，请检查爱快路由器连接"}

@router.post("/toggle-record")
def toggle_record(body: dict, session: dict = Depends(verify_session), _csrf: None = Depends(verify_csrf_token)):
    """
    启用或停用指定 DNS 记录。

    Args:
        body: {"id": str|int, "enable": bool}
    """
    service = _get_ikuai_service()
    if not service:
        return {"success": False, "message": "爱快 DNS 功能未启用"}

    record_id = body.get("id")
    enable = body.get("enable", True)

    if record_id is None:
        return {"success": False, "message": "缺少记录 ID（id 字段）"}

    if enable:
        success = service.enable_dns_record(record_id)
    else:
        success = service.disable_dns_record(record_id)

    service.close()

    action = "启用" if enable else "停用"
    if success:
        return {"success": True, "message": f"DNS 记录已{action}（ID={record_id}）"}
    else:
        return {"success": False, "message": f"DNS 记录{action}失败，请检查爱快路由器连接"}
