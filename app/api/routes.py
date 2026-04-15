from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, status, Query, Form
import yaml
import os
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import re
from croniter import croniter
from urllib.parse import urlparse
import time
import copy
import secrets
import string

from app.services.cloudflare_speed_test import CloudflareSpeedTestService
from app.services.hosts_manager import HostsManager
from app.services.scheduler import SchedulerService
from app.services.torrent_clients import TorrentClientManager
from datetime import datetime
from app.models import User
from app.utils import notify as notify_module

from app.auth import get_password_hash, verify_password, get_current_user
from version import get_version

CONFIG_PATH = "config/config.yaml"
DEFAULT_CLOUDFLARE_IP = "104.16.91.215"  # 全局默认Cloudflare IP

logger = logging.getLogger(__name__)

TASK_NOTIFY_TITLE_MAP = {
    "IP优选与Hosts更新": "🚀 IP优选与Hosts更新",
    "仅更新Hosts": "🛠️ 仅更新Hosts",
    "清空并更新Hosts": "🧹 清空并更新Hosts",
}

STRICT_NOTIFY_TYPE_KEY_MAPPING = {
    "webhook": ["WEBHOOK_URL", "WEBHOOK_METHOD", "WEBHOOK_BODY", "WEBHOOK_HEADERS", "WEBHOOK_CONTENT_TYPE"],
    "telegram": ["TG_BOT_TOKEN", "TG_USER_ID", "TG_API_HOST", "TG_PROXY_AUTH", "TG_PROXY_HOST", "TG_PROXY_PORT"],
    "wecom_bot": ["QYWX_KEY", "QYWX_ORIGIN"],
    "wecom_app": ["QYWX_AM"],
    "smtp": ["SMTP_SERVER", "SMTP_SSL", "SMTP_EMAIL", "SMTP_PASSWORD", "SMTP_NAME"],
    "bark": ["BARK_PUSH", "BARK_ARCHIVE", "BARK_GROUP", "BARK_SOUND", "BARK_ICON", "BARK_LEVEL", "BARK_URL"],
    "wxpusher": ["WXPUSHER_APP_TOKEN", "WXPUSHER_TOPIC_IDS", "WXPUSHER_UIDS"],
    "gotify": ["GOTIFY_URL", "GOTIFY_TOKEN", "GOTIFY_PRIORITY"],
    "mediasaber": ["MEDIASABER_HOST", "MEDIASABER_APIKEY"],
}

TASK_NOTIFY_MINIMAL_KEYS_SETS = [
    ("WEBHOOK_URL", "WEBHOOK_METHOD"),
    ("QYWX_KEY",),
    ("TG_BOT_TOKEN", "TG_USER_ID"),
    ("SMTP_SERVER", "SMTP_EMAIL", "SMTP_PASSWORD"),
    ("BARK_PUSH",),
    ("WXPUSHER_APP_TOKEN",),
    ("GOTIFY_URL", "GOTIFY_TOKEN"),
    ("MEDIASABER_HOST", "MEDIASABER_APIKEY"),
]

TEST_NOTIFY_MINIMAL_KEYS_SETS = [
    ("WEBHOOK_URL", "WEBHOOK_METHOD"),
    ("QYWX_KEY",),
    ("QYWX_AM",),
    ("TG_BOT_TOKEN", "TG_USER_ID"),
    ("SMTP_SERVER", "SMTP_EMAIL", "SMTP_PASSWORD"),
    ("BARK_PUSH",),
    ("PUSH_KEY",),
    ("IGOT_PUSH_KEY",),
    ("FSKEY",),
    ("DD_BOT_TOKEN", "DD_BOT_SECRET"),
    ("CHAT_URL", "CHAT_TOKEN"),
    ("MEDIASABER_HOST", "MEDIASABER_APIKEY"),
]


def _extract_task_status(text: str) -> tuple[str, str]:
    success_markers = ["完成", "success", "已更新", "已完成", "成功"]
    failed_markers = ["失败", "error", "异常"]

    status_emoji = "ℹ️"
    status_text = "执行结果：请查看详情"
    if any(m in text for m in success_markers):
        status_emoji = "✅"
        status_text = "执行结果：任务完成"
    if any(m in text for m in failed_markers):
        status_emoji = "❌"
        status_text = "执行结果：任务失败"
    return status_emoji, status_text


def _parse_hosts_update_summary(line: str) -> Optional[tuple[str, str]]:
    match = re.search(r"成功更新hosts文件[，,]添加了(\d+)条记录[，,]共(\d+)个分区", line)
    if not match:
        return None
    return match.group(1), match.group(2)


def _sync_main_config(config_data: Dict[str, Any], success_message: Optional[str] = None, failure_prefix: str = "同步全局config对象失败"):
    try:
        import app.main
        app.main.config = config_data
        if success_message:
            logger.info(success_message)
    except Exception as e:
        logger.error(f"{failure_prefix}: {str(e)}")


def _flatten_notify_channel(ch_conf: Dict[str, Any], notify_cfg: Dict[str, Any], strict_by_type: bool = False) -> Dict[str, Any]:
    channel_type = ch_conf.get("type", "").lower()
    required_keys = STRICT_NOTIFY_TYPE_KEY_MAPPING.get(channel_type, []) if strict_by_type else []
    flat: Dict[str, Any] = {}

    for k, v in ch_conf.items():
        if k in ("name", "type", "enable"):
            continue
        if required_keys and k.upper() not in required_keys:
            continue
        flat[k] = v

    if "HITOKOTO" in ch_conf:
        val = ch_conf.get("HITOKOTO")
        flat["HITOKOTO"] = ("true" if val else "false") if isinstance(val, bool) else val
    else:
        global_hitokoto = notify_cfg.get("hitokoto", True)
        flat["HITOKOTO"] = "true" if bool(global_hitokoto) else "false"

    return flat


def _is_valid_notify_payload(flat: Dict[str, Any], minimal_keys_sets: List[tuple[str, ...]]) -> bool:
    return any(all(flat.get(k) for k in keys) for keys in minimal_keys_sets)


def _queue_cfst_update_task(background_tasks: BackgroundTasks, hosts_manager: HostsManager, startup_message: str):
    def combined_task():
        logger.info("手动执行组合任务：优选IP + 更新tracker + 更新hosts（严格串行）")
        ok, notify_msg = hosts_manager.run_cfst_and_update_hosts()
        status = hosts_manager.get_task_status() if hasattr(hosts_manager, 'get_task_status') else {}
        short_msg = status.get('message') if isinstance(status, dict) else ("执行完成" if ok else "执行失败")
        log_msg = short_msg.split('\n')[0] if short_msg else ""
        logger.info(f"[任务通知] IP优选与Hosts更新 -> {log_msg}")
        _send_task_notify("IP优选与Hosts更新", notify_msg)

    background_tasks.add_task(combined_task)
    return {"message": startup_message}


def _format_ip_optimize_notify_content(title: str, text: str, time_text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    old_ip = "-"
    new_ip = "-"
    duration = "-"
    tracker_count = "-"
    hosts_count = "-"
    fallback_lines: List[str] = []
    other_lines: List[str] = []

    for line in lines:
        if line.startswith("旧 IP 为："):
            old_ip = line.split("：", 1)[1].strip() or "-"
        elif line.startswith("新 IP 为："):
            new_ip = line.split("：", 1)[1].strip() or "-"
        elif line.startswith("测速耗时："):
            duration = line.split("：", 1)[1].strip() or "-"
        elif line.startswith("已更新："):
            match = re.search(r"已更新：\s*(\d+)\s*个Tracker和\s*(\d+)\s*条hosts记录", line)
            if match:
                tracker_count = match.group(1)
                hosts_count = match.group(2)
            else:
                other_lines.append(line)
        elif line == "兜底详情：":
            continue
        elif line.startswith("✅ 保留：") or line.startswith("❌ 丢弃：") or line.startswith("IP："):
            fallback_lines.append(line)
        elif line != "Cloudflare优选完成！":
            other_lines.append(line)

    status_emoji, status_text = _extract_task_status(text)
    sections = [
        "【🚀 IP优选与Hosts更新】",
        "──────────",
        f"📌 任务类型：{title}",
        f"{status_emoji} {status_text}",
        "──────────",
        "📊 优选结果：",
        f"• 旧 IP：{old_ip}",
        f"• 新 IP：{new_ip}",
        f"• 测速耗时：{duration}",
        f"• Tracker 更新数：{tracker_count}",
        f"• Hosts 记录数：{hosts_count}",
    ]

    if fallback_lines:
        sections.extend([
            "──────────",
            "🧩 兜底详情：",
            *fallback_lines,
        ])

    if other_lines:
        sections.extend([
            "──────────",
            "📝 补充说明：",
            *other_lines,
        ])

    sections.extend([
        "──────────",
        f"⏰ 推送时间：{time_text}",
    ])

    return "\n".join(sections)

def _format_generic_task_notify_content(title: str, text: str, time_text: str) -> str:
    task_heading_map = {
        "仅更新Hosts": "【🛠️ 仅更新Hosts】",
        "清空并更新Hosts": "【🧹 清空并更新Hosts】",
    }
    detail_heading_map = {
        "仅更新Hosts": "📄 更新详情：",
        "清空并更新Hosts": "🧼 清理详情：",
    }
    status_emoji, status_text = _extract_task_status(text)
    raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
    detail_lines: List[str] = []

    for line in raw_lines:
        if title == "仅更新Hosts":
            summary = _parse_hosts_update_summary(line)
            if summary:
                detail_lines.append("• 成功更新hosts文件")
                detail_lines.append(f"• 添加了{summary[0]}条记录")
                detail_lines.append(f"• 共{summary[1]}个分区")
                continue
        if title == "清空并更新Hosts":
            summary = _parse_hosts_update_summary(line)
            if summary:
                detail_lines.append("• 已清理项目分区")
                detail_lines.append("• 成功更新hosts文件")
                detail_lines.append(f"• 添加了{summary[0]}条记录")
                detail_lines.append(f"• 共{summary[1]}个分区")
                continue
        detail_lines.append(line if line.startswith("•") else f"• {line}")

    detail_block = "\n".join(detail_lines) if detail_lines else "无详细信息"

    return (
        f"{task_heading_map.get(title, f'【📣 {title}】')}\n"
        f"──────────\n"
        f"📌 任务类型：{title}\n"
        f"{status_emoji} {status_text}\n"
        f"──────────\n"
        f"{detail_heading_map.get(title, '📄 详细信息：')}\n"
        f"{detail_block}\n"
        f"──────────\n"
        f"⏰ 推送时间：{time_text}"
    )

def _format_task_notify_content(title: str, content: str) -> str:
    text = str(content or "").strip()
    time_text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if title == "IP优选与Hosts更新":
        return _format_ip_optimize_notify_content(title, text, time_text)

    return _format_generic_task_notify_content(title, text, time_text)

def _send_task_notify(title: str, content: str):
    try:
        pretty_title = ""
        pretty_content = _format_task_notify_content(title, content)

        cfg = get_config() or {}
        notify_cfg = copy.deepcopy(cfg.get("notify", {}))
        channels = notify_cfg.get("channels", {}) or {}

        payloads: list[Dict[str, Any]] = []
        if isinstance(channels, dict):
            for _, ch_conf in channels.items():
                if isinstance(ch_conf, dict) and ch_conf.get("enable"):
                    flat_config = _flatten_notify_channel(ch_conf, notify_cfg, strict_by_type=True)
                    channel_type = ch_conf.get("type", "").lower()
                    if channel_type:
                        flat_config[f"ENABLE_{channel_type.upper()}"] = ch_conf.get("enable", False)
                    payloads.append(flat_config)

        valid = []
        for flat in payloads:
            if _is_valid_notify_payload(flat, TASK_NOTIFY_MINIMAL_KEYS_SETS):
                valid.append(flat)

        for flat in valid:
            notify_module.send(pretty_title, pretty_content, ignore_default_config=True, **flat)
    except Exception as e:
        logger.error(f"发送任务结果通知失败: {e}", exc_info=True)


router = APIRouter()

from app.globals import get_hosts_manager, get_cloudflare_service, get_scheduler_service, get_torrent_client_manager

def get_config():
    """从文件获取最新配置"""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}
    return {}

# 获取配置（前端拉取用，每次从文件读取）
@router.get("/config")
async def get_config_api():
    """每次都从文件读取最新配置，防止内存与文件不同步导致tracker状态异常"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    else:
        return {}

# 更新配置（CRON表达式校验）
@router.post("/config")
async def update_config(
    config_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    hosts_manager: HostsManager = Depends(get_hosts_manager),
    cloudflare_service: CloudflareSpeedTestService = Depends(get_cloudflare_service),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """更新配置"""
    try:
        old_config = get_config()
        # CRON表达式校验
        cron_expr = config_data.get("cloudflare", {}).get("cron", "0 0 * * *")
        if not croniter.is_valid(cron_expr):
            raise HTTPException(status_code=400, detail="CRON表达式无效，请检查格式")
        
        # 保存配置
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)

        old_hosts_sources = old_config.get("hosts_sources", []) if isinstance(old_config, dict) else []
        new_hosts_sources = config_data.get("hosts_sources", []) if isinstance(config_data, dict) else []
        old_source_enable_map = {
            s.get("url"): bool(s.get("enable", True))
            for s in old_hosts_sources
            if isinstance(s, dict) and s.get("url")
        }
        source_disabled = any(
            old_source_enable_map.get(s.get("url"), False) and not bool(s.get("enable", True))
            for s in new_hosts_sources
            if isinstance(s, dict) and s.get("url")
        )
        if old_hosts_sources != new_hosts_sources:
            hosts_manager.clear_merged_hosts_backup()
        
        # 更新服务配置
        hosts_manager.update_config(config_data)
        cloudflare_service.update_config(config_data)

        _sync_main_config(config_data, "配置更新API已同步刷新全局config对象", "配置更新API刷新全局config对象失败")
        
        # 重启调度器
        scheduler_service.stop()
        scheduler_service.update_config(config_data)
        scheduler_service.start()

        if source_disabled:
            logger.info("检测到hosts源被关闭，后台立即触发一次hosts重建")
            background_tasks.add_task(hosts_manager.update_hosts)
        
        return {"message": "配置已更新"}
    except Exception as e:
        logger.error(f"更新配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")

# 获取认证状态
@router.get("/auth/status")
async def get_auth_status(current_user: Optional[User] = Depends(get_current_user)):
    config = get_config()
    auth_enable = config.get("auth", {}).get("enable", False)
    
    # 如果认证未启用，视为已认证（作为guest或admin）
    if not auth_enable:
        return {
            "is_authenticated": True,
            "user": {"username": "guest", "is_authenticated": True},
            "auth_enabled": False
        }
    
    return {
        "is_authenticated": current_user.is_authenticated if current_user else False,
        "user": current_user,
        "auth_enabled": True
    }

# 新增：更新认证配置的 API
@router.post("/auth/config", dependencies=[Depends(get_current_user)])
async def update_auth_config(
    request: Request,
    enable_auth: bool = Form(None),
    username: str = Form(None),
    current_password: str = Form(None),
    new_password: str = Form(None),
    confirm_password: str = Form(None),
    current_user: User = Depends(get_current_user)
):
    """更新认证配置，包括启用/禁用、用户名和密码"""
    logger.info(f"收到认证配置更新请求: enable_auth={enable_auth}, username={username}, has_current_password={bool(current_password)}, has_new_password={bool(new_password)}")
    current_config = get_config()
    
    if current_config.get("auth", {}).get("enable") and (not current_user or current_user.username == "guest"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改认证配置")

    auth_settings = current_config.get("auth", {}).copy()
    config_changed = False

    if enable_auth is not None and enable_auth != auth_settings.get("enable"):
        auth_settings["enable"] = enable_auth
        config_changed = True
        logger.info(f"登录认证已 {'启用' if enable_auth else '禁用'}")

        # 如果启用认证且没有设置密码，也没有提供新密码，则生成随机密码
        if enable_auth and not auth_settings.get("password_hash") and not new_password:
            alphabet = string.ascii_letters + string.digits
            generated_password = ''.join(secrets.choice(alphabet) for i in range(12))
            auth_settings["password_hash"] = get_password_hash(generated_password)
            
            # 确保设置默认用户名（如果不存在且未在本次请求中提供）
            if not auth_settings.get("username") and not username:
                auth_settings["username"] = "admin"
                logger.info("未设置用户名，已默认设置为: admin")
            
            logger.info(f"已自动生成随机初始密码: {generated_password}")
            logger.warning("请务必保存此密码！它只会在日志中显示一次。")

    if username and username != auth_settings.get("username"):
        auth_settings["username"] = username
        config_changed = True
        logger.info(f"登录用户名已修改为: {username}")

    if new_password:
        # 验证新密码长度
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="新密码长度至少需要8位字符")
        
        # 检查新密码与确认密码是否匹配
        if new_password != confirm_password:
            raise HTTPException(status_code=400, detail="新密码与确认密码不匹配")
        
        if not current_password:
            # 如果没有提供当前密码，检查是否允许这样做
            # 使用原始配置检查认证是否启用，因为auth_settings可能已被修改
            original_enable = current_config.get("auth", {}).get("enable")
            if not auth_settings.get("password_hash") or not original_enable:
                # 首次设置密码或认证被禁用时可以不需要当前密码
                auth_settings["password_hash"] = get_password_hash(new_password)
                config_changed = True
                logger.info("登录密码已设置/更新。")
            else:
                raise HTTPException(status_code=400, detail="修改密码需要提供当前密码。如果您忘记了当前密码，请联系管理员。")
        else:
            # 验证当前密码
            if not auth_settings.get("password_hash"):
                raise HTTPException(status_code=400, detail="当前系统中没有设置密码，请清空当前密码字段后重试")
            elif not verify_password(current_password, auth_settings.get("password_hash", "")):
                raise HTTPException(status_code=400, detail="当前密码错误，请检查并重新输入")
            else:
                # 当前密码正确，更新为新密码
                auth_settings["password_hash"] = get_password_hash(new_password)
                config_changed = True
                logger.info("登录密码已修改") 
                # 密码修改成功，使当前会话失效，强制重新登录
                request.session.pop("user", None) 

    if config_changed:
        current_config["auth"] = auth_settings
        try:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                yaml.dump(current_config, f, default_flow_style=False, allow_unicode=True)
            
            # 重新加载全局配置，确保认证配置变更立即生效
            from app.auth import reload_global_config
            if reload_global_config():
                logger.info("全局配置已重新加载，认证配置变更立即生效")
            else:
                logger.warning("全局配置重新加载失败，部分功能可能需要重启才能生效")
            
            # 重要：如果认证相关配置发生变化，清除当前session，强制重新登录
            # 这确保新的认证配置能够立即生效
            request.session.clear()
            
            message = "认证配置已更新。"
            # 根据具体更改调整消息，并处理会话
            if enable_auth is not None and not auth_settings.get("enable"):
                message += " 登录认证已禁用，您已自动登出。"
            elif new_password:
                 message += " 密码已更改，您已自动登出，请使用新密码重新登录。"
            elif username and username != current_user.username:
                 message += " 用户名已更改，您已自动登出，请重新登录。"
            else:
                message += " 为确保配置立即生效，您已自动登出，请重新登录。"
            
            return {"message": message}
        except Exception as e:
            logger.error(f"更新认证配置失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"更新认证配置失败: {str(e)}")
    
    return {"message": "未检测到配置更改"}

# 手动运行CloudflareSpeedTest
@router.post("/run-cloudflare-test")
async def run_cloudflare_test(
    background_tasks: BackgroundTasks,
    hosts_manager: HostsManager = Depends(get_hosts_manager)
):
    """手动运行CloudflareSpeedTest和更新hosts源（严格串行）"""
    try:
        return _queue_cfst_update_task(background_tasks, hosts_manager, "IP优选与Hosts更新任务已启动（严格串行）")
    except Exception as e:
        logger.error(f"启动组合任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动组合任务失败: {str(e)}")

# 获取调度器状态
@router.get("/scheduler-status")
async def get_scheduler_status(
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """获取调度器状态"""
    return {
        "running": scheduler_service.is_running(),
        "jobs": scheduler_service.get_jobs()
    }

# 兼容旧版前端，避免404错误
@router.get("/last-result")
async def get_last_result_compatibility():
    """兼容旧版前端，返回空结果"""
    return {
        "success": False,
        "message": "此API端点已弃用，优选结果不再显示",
        "time": "",
        "results": []
    }

# 任务状态API
@router.get("/task-status")
async def get_task_status(
    hosts_manager: HostsManager = Depends(get_hosts_manager),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """获取当前任务状态
    
    前端轮询此接口以获取后台任务的执行状态
    
    Returns:
        任务状态：
        - status: done | running
        - message: 任务状态描述
    """
    try:
        # 首先检查scheduler_service中的任务状态
        scheduler_status = getattr(scheduler_service, 'get_task_status', lambda: {"status": "done", "message": "无任务"})()
        if scheduler_status.get("status") == "running":
            return scheduler_status
            
        # 然后检查hosts_manager中的任务状态
        hosts_status = hosts_manager.get_task_status()
        if hosts_status.get("status") == "running":
            return hosts_status
            
        # 如果都没有运行中的任务，返回默认完成状态
        return {
            "status": "done",
            "message": "无正在运行的任务"
        }
    except Exception as e:
        logger.error(f"获取任务状态时出错: {str(e)}", exc_info=True)
        # 返回安全的默认状态
        return {
            "status": "done",
            "message": "获取任务状态出错，请检查日志"
        }

# 获取日志
@router.get("/logs")
async def get_logs(lines: int = 1000):
    """获取最近的日志，统一按UTF-8读取并返回字符串，避免分块解码导致的乱码。"""
    log_file = "logs/app.log"
    try:
        if not os.path.exists(log_file):
            return {"logs": ""}

        # 使用 UTF-8 严格解码，遇到异常字符以替换符显示，避免抛错
        from collections import deque
        dq = deque(maxlen=max(10, lines))
        with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                dq.append(line.rstrip('\n'))
        return {"logs": "\n".join(list(dq)[-lines:])}
    except Exception as e:
        logger.error(f"获取日志失败: {str(e)}")
        return {"logs": "日志读取失败，请检查日志文件权限和编码"}

@router.post("/logs/clear")
async def clear_logs():
    """清空日志文件内容"""
    try:
        log_file = "logs/app.log"
        # 确保目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        # 以写模式截断文件
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("")
        logger.info("日志文件已被清空")
        return {"success": True, "message": "日志已清空"}
    except Exception as e:
        logger.error(f"清空日志失败: {str(e)}")
        return {"success": False, "message": f"清空日志失败: {str(e)}"}

# ===== Cloudflare白名单管理API =====

@router.get("/cloudflare-domains")
async def get_cloudflare_domains():
    config = get_config()
    domains = config.get("cloudflare_domains", [])
    return {"cloudflare_domains": domains}

@router.post("/cloudflare-domains")
async def add_cloudflare_domain(background_tasks: BackgroundTasks, domain: str = Query(..., description="要添加的Cloudflare域名")):
    config = get_config()
    domains = set(config.get("cloudflare_domains", []))
    domains.add(domain.strip().lower())
    config["cloudflare_domains"] = list(domains)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    hosts_manager = get_hosts_manager()
    hosts_manager.update_config(config)
    _sync_main_config(config)
    background_tasks.add_task(hosts_manager.update_hosts)
    return {"message": f"已添加 {domain} 到Cloudflare白名单", "cloudflare_domains": list(domains)}

@router.delete("/cloudflare-domains")
async def delete_cloudflare_domain(background_tasks: BackgroundTasks, domain: str = Query(..., description="要删除的Cloudflare域名")):
    config = get_config()
    domains = set(config.get("cloudflare_domains", []))
    domains.discard(domain.strip().lower())
    config["cloudflare_domains"] = list(domains)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    hosts_manager = get_hosts_manager()
    hosts_manager.update_config(config)
    _sync_main_config(config)
    background_tasks.add_task(hosts_manager.update_hosts)
    return {"message": f"已从Cloudflare白名单移除 {domain}", "cloudflare_domains": list(domains)}

# 修改添加tracker接口，支持force_cloudflare参数
@router.post("/trackers")
async def add_tracker(
    tracker: dict,
    background_tasks: BackgroundTasks,
    hosts_manager: HostsManager = Depends(get_hosts_manager),
    force_cloudflare: bool = False
):
    try:
        domain = tracker.get("domain", "")
        if domain:
            domain = re.sub(r"^https?://", "", domain, flags=re.IGNORECASE)
            domain = domain.split("/")[0]
            tracker["domain"] = domain
        config = get_config()
        if "trackers" not in config:
            config["trackers"] = []
        for existing in config["trackers"]:
            if existing["domain"] == tracker["domain"]:
                raise HTTPException(status_code=400, detail="Tracker已存在")
        ip_set = set()
        for t in config["trackers"]:
            if t.get("enable") and t.get("ip"):
                ip_set.add(t["ip"])
        if len(ip_set) > 1:
            raise HTTPException(status_code=400, detail="检测到现有Tracker的IP不一致，请先统一所有Tracker的IP后再添加。")
        elif len(ip_set) == 1:
            default_ip = list(ip_set)[0]
        else:
            default_ip = hosts_manager.best_cloudflare_ip or "104.16.91.215"
        tracker["ip"] = default_ip
        config["trackers"].append(tracker)
        if force_cloudflare:
            domains = set(config.get("cloudflare_domains", []))
            domains.add(domain.strip().lower())
            config["cloudflare_domains"] = list(domains)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        hosts_manager.update_config(config)
        background_tasks.add_task(hosts_manager.update_hosts)
        _sync_main_config(config)
        return {"message": "Tracker已添加，Hosts更新任务已在后台启动"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加Tracker失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加Tracker失败: {str(e)}")

@router.delete("/trackers/{domain}")
async def delete_tracker(
    domain: str,
    background_tasks: BackgroundTasks,
    hosts_manager: HostsManager = Depends(get_hosts_manager)
):
    """删除Tracker"""
    try:
        # 更新配置
        config = get_config()
        if "trackers" not in config:
            raise HTTPException(status_code=404, detail="Tracker不存在")

        config["trackers"] = [t for t in config["trackers"] if t["domain"] != domain]
        hosts_manager.remove_tracker_domain(domain)
        
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        hosts_manager.update_config(config)
        _sync_main_config(config, "删除Tracker API已同步刷新全局config对象，确保前端获取到最新数据", "删除Tracker API刷新全局config对象失败")
        background_tasks.add_task(hosts_manager.update_hosts)
        
        return {"message": "Tracker已删除，Hosts更新任务已在后台启动"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除Tracker失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除Tracker失败: {str(e)}")

# 添加hosts源（URL校验）
@router.post("/hosts-sources")
async def add_hosts_source(
    source: Dict[str, Any],
    background_tasks: BackgroundTasks,  # 新增参数
    hosts_manager: HostsManager = Depends(get_hosts_manager)
):
    """添加hosts源"""
    try:
        url = source.get("url", "")
        if url and not re.match(r"^https?://", url, re.IGNORECASE):
            url = "https://" + url
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise HTTPException(status_code=400, detail="Hosts源URL无效，请检查格式")
        source["url"] = url
        config = get_config()
        if "hosts_sources" not in config:
            config["hosts_sources"] = []
        for existing in config["hosts_sources"]:
            if existing["url"] == source["url"]:
                raise HTTPException(status_code=400, detail="hosts源已存在")
        config["hosts_sources"].append(source)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        hosts_manager.update_config(config)
        _sync_main_config(config, "添加hosts源API已同步刷新全局config对象，确保前端获取到最新数据", "添加hosts源API刷新全局config对象失败")
        background_tasks.add_task(hosts_manager.update_hosts)
        return {"message": "hosts源已添加，正在后台更新hosts"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加hosts源失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加hosts源失败: {str(e)}")

@router.delete("/hosts-sources")
async def delete_hosts_source(
    url: str,
    background_tasks: BackgroundTasks,  # 新增参数
    hosts_manager: HostsManager = Depends(get_hosts_manager)
):
    """删除hosts源"""
    try:
        config = get_config()
        if "hosts_sources" not in config:
            raise HTTPException(status_code=404, detail="hosts源不存在")
        config["hosts_sources"] = [s for s in config["hosts_sources"] if s["url"] != url]
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
        hosts_manager.update_config(config)
        _sync_main_config(config, "删除hosts源API已同步刷新全局config对象，确保前端获取到最新数据", "删除hosts源API刷新全局config对象失败")
        background_tasks.add_task(hosts_manager.update_hosts)
        return {"message": "hosts源已删除，正在后台更新hosts"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除hosts源失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除hosts源失败: {str(e)}")

# 手动更新hosts
@router.post("/update-hosts")
async def update_hosts(
    background_tasks: BackgroundTasks,
    hosts_manager: HostsManager = Depends(get_hosts_manager)
):
    """手动更新hosts"""
    try:
        def task():
            ok = hosts_manager.update_hosts()
            status = hosts_manager.get_task_status() if hasattr(hosts_manager, 'get_task_status') else {}
            msg = status.get('message') if isinstance(status, dict) else ("更新完成" if ok else "更新失败")
            log_msg = msg.split('\n')[0] if msg else ""
            logger.info(f"[任务通知] 仅更新Hosts -> {log_msg}")
            _send_task_notify("仅更新Hosts", msg)
        background_tasks.add_task(task)
        return {"message": "hosts更新任务已启动"}
    except Exception as e:
        logger.error(f"更新hosts失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新hosts失败: {str(e)}")

# 获取当前hosts
@router.get("/current-hosts")
async def get_current_hosts(
    hosts_manager: HostsManager = Depends(get_hosts_manager)
):
    """获取当前hosts"""
    try:
        return {"hosts": hosts_manager.read_system_hosts()}
    except Exception as e:
        logger.error(f"获取hosts失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取hosts失败: {str(e)}")

# ===== 备份管理API =====

@router.post("/backup/test")
async def test_backup_connection(
    config: Dict[str, Any]
):
    """测试WebDav连接"""
    try:
        from app.services.backup_service import BackupService
        service = BackupService()
        
        url = config.get("webdav_url")
        username = config.get("webdav_username")
        password = config.get("webdav_password")
        
        if service.test_connection(url, username, password):
            return {"success": True, "message": "连接测试成功"}
        else:
            return {"success": False, "message": "连接测试失败，请检查配置"}
    except Exception as e:
        logger.error(f"测试连接失败: {str(e)}")
        return {"success": False, "message": f"测试连接失败: {str(e)}"}

@router.post("/backup/run")
async def run_backup(
    background_tasks: BackgroundTasks
):
    """手动执行备份"""
    try:
        def backup_task():
            from app.services.backup_service import BackupService
            service = BackupService()
            config = get_config()
            if service.backup_config(config):
                logger.info("手动备份成功")
            else:
                logger.error("手动备份失败")
        
        background_tasks.add_task(backup_task)
        return {"message": "备份任务已启动"}
    except Exception as e:
        logger.error(f"启动备份任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动备份任务失败: {str(e)}")

@router.get("/backup/list")
async def list_backups():
    """获取备份列表"""
    try:
        from app.services.backup_service import BackupService
        service = BackupService()
        config = get_config()
        backups = service.list_backups(config)
        return {"success": True, "backups": backups}
    except Exception as e:
        logger.error(f"获取备份列表失败: {str(e)}")
        return {"success": False, "message": f"获取备份列表失败: {str(e)}"}

@router.post("/backup/restore")
async def restore_backup(payload: Dict[str, Any], hosts_manager: HostsManager = Depends(get_hosts_manager)):
    """恢复备份"""
    try:
        filename = payload.get("filename")
        if not filename:
            return {"success": False, "message": "未指定文件名"}
            
        from app.services.backup_service import BackupService
        service = BackupService()
        config = get_config()
        
        if service.restore_backup(config, filename):
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    new_config = yaml.safe_load(f)
                hosts_manager.update_config(new_config)
                _sync_main_config(new_config)
            except Exception as e:
                logger.error(f"重载配置失败: {e}")
                
            return {"success": True, "message": "配置已恢复，建议刷新页面"}
        else:
            return {"success": False, "message": "恢复失败，请查看日志"}
    except Exception as e:
        logger.error(f"恢复备份失败: {str(e)}")
        return {"success": False, "message": f"恢复备份失败: {str(e)}"}

# ===== 添加新的模型和API端点 =====

class DomainList(BaseModel):
    domains: List[str]

# 批量添加PT站点域名
@router.post("/batch-add-domains")
async def batch_add_domains(
    request: Request,
    background_tasks: BackgroundTasks,
    hosts_manager: HostsManager = Depends(get_hosts_manager)
):
    """批量添加域名"""
    try:
        data = await request.json()
        domains_data = data.get("domains", "")

        if isinstance(domains_data, list):
            domains = domains_data
        else:
            domains = domains_data.strip().split("\n")

        domains = [domain.strip() for domain in domains if domain and domain.strip()]

        cleaned_domains = []
        for domain in domains:
            d = re.sub(r"^https?://", "", domain, flags=re.IGNORECASE)
            d = d.split("/")[0]
            cleaned_domains.append(d)
        domains = cleaned_domains
        
        if not domains:
            return {"status": "warning", "message": "没有提供有效的域名"}
        
        config = get_config()
        if "trackers" not in config:
            config["trackers"] = []

        ip_set = set()
        for t in config["trackers"]:
            if t.get("enable") and t.get("ip"):
                ip_set.add(t["ip"])
                
        if len(ip_set) > 1:
            return {"status": "error", "message": "检测到现有Tracker的IP不一致，请先统一所有Tracker的IP后再添加。"}
        
        if len(ip_set) == 1:
            default_ip = list(ip_set)[0]
        else:
            default_ip = hosts_manager.best_cloudflare_ip or "104.16.91.215"

        added = []
        skipped = []

        for domain in domains:
            if any(t["domain"] == domain for t in hosts_manager.config.setdefault("trackers", [])):
                skipped.append(domain)
                continue

            hosts_manager.config["trackers"].append({
                "name": domain,
                "domain": domain,
                "ip": default_ip,
                "enable": True
            })
            added.append(domain)
            
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(hosts_manager.config, f, default_flow_style=False, allow_unicode=True)
        _sync_main_config(hosts_manager.config, "批量添加域名API已同步刷新全局config对象，确保前端获取到最新数据", "批量添加域名API刷新全局config对象失败")
        background_tasks.add_task(hosts_manager.update_hosts)

        message = f"批量添加完成：成功添加 {len(added)} 个域名，跳过 {len(skipped)} 个已存在的域名"
        details = {
            "added": added,
            "skipped": skipped
        }
        
        return {
            "status": "success", 
            "message": message,
            "details": details
        }
    except Exception as e:
        logger.error(f"批量添加域名失败: {str(e)}")
        return {"status": "error", "message": f"批量添加域名失败: {str(e)}"}

# 运行CloudflareSpeedTest优选脚本
@router.post("/run-cfst-script")
async def run_cfst_script(
    background_tasks: BackgroundTasks,
    hosts_manager: HostsManager = Depends(get_hosts_manager)
):
    """运行CloudflareSpeedTest优选脚本和更新hosts源（严格串行）"""
    try:
        return _queue_cfst_update_task(background_tasks, hosts_manager, "IP优选与Hosts更新任务已启动（严格串行）")
    except Exception as e:
        logger.error(f"启动组合任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动组合任务失败: {str(e)}")

# 手动更新所有Tracker为最佳IP
@router.post("/update-all-trackers")
async def update_all_trackers(
    ip: str,
    hosts_manager: HostsManager = Depends(get_hosts_manager)
):
    """手动更新所有Tracker为指定IP"""
    try:
        hosts_manager._update_all_trackers_ip(ip)
        hosts_manager.update_hosts()
        
        _sync_main_config(hosts_manager.config, "API端点已同步刷新全局config对象，确保前端获取到最新数据", "API端点刷新全局config对象失败")
            
        return {"message": f"已将所有Tracker的IP更新为 {ip}"}
    except Exception as e:
        logger.error(f"更新所有Tracker的IP失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新所有Tracker的IP失败: {str(e)}")

# ===== 下载器相关API =====

# 获取下载器客户端列表
@router.get("/torrent-clients")
async def get_torrent_clients(config: Dict[str, Any] = Depends(get_config)):
    """获取所有下载器客户端配置"""
    try:
        clients_config = config.get("torrent_clients", [])
        # 兼容旧配置格式
        if isinstance(clients_config, dict):
            converted_clients = []
            for client_type, client_config in clients_config.items():
                converted_clients.append({
                    "id": f"{client_type}_migrated",
                    "name": f"{client_type.capitalize()} (迁移)",
                    "type": client_type,
                    **client_config
                })
            clients_config = converted_clients
        
        return {"success": True, "clients": clients_config}
    except Exception as e:
        logger.error(f"获取下载器客户端列表失败: {str(e)}")
        return {"success": False, "message": f"获取客户端列表失败: {str(e)}"}

# 保存下载器客户端配置
@router.post("/torrent-clients")
async def save_torrent_clients(
    clients_data: dict,
    config: Dict[str, Any] = Depends(get_config)
):
    """保存下载器客户端配置"""
    try:
        clients_config = clients_data.get("clients", [])
        
        # 验证每个客户端配置
        for client in clients_config:
            # 必填字段验证
            if not client.get("id"):
                return {"success": False, "message": "客户端ID不能为空"}
            if not client.get("name"):
                return {"success": False, "message": "客户端名称不能为空"}
            if not client.get("type") in ["qbittorrent", "transmission"]:
                return {"success": False, "message": "不支持的客户端类型"}
            if not client.get("host"):
                return {"success": False, "message": "主机地址不能为空"}
            
            # 主机地址验证
            host = client.get("host", "")
            if not re.match(r"^(?:[a-zA-Z0-9\-\.]+|\d{1,3}(?:\.\d{1,3}){3})$", host):
                return {"success": False, "message": f"客户端 {client.get('name')} 的主机地址无效"}
            
            # 端口验证
            try:
                port = int(client.get("port", 0))
                if not (1 <= port <= 65535):
                    return {"success": False, "message": f"客户端 {client.get('name')} 的端口范围无效(1-65535)"}
            except (ValueError, TypeError):
                return {"success": False, "message": f"客户端 {client.get('name')} 的端口必须为数字"}
        
        # 检查ID唯一性
        client_ids = [client.get("id") for client in clients_config]
        if len(client_ids) != len(set(client_ids)):
            return {"success": False, "message": "客户端ID不能重复"}
        
        # 更新配置
        config["torrent_clients"] = clients_config
        
        # 保存配置到文件
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        # 更新 TorrentClientManager
        torrent_client_manager = get_torrent_client_manager()
        torrent_client_manager.update_config(config)
        
        logger.info(f"下载器客户端配置已保存，共 {len(clients_config)} 个客户端")
        return {"success": True, "message": f"下载器配置已保存，共 {len(clients_config)} 个客户端"}
        
    except Exception as e:
        logger.error(f"保存下载器客户端配置失败: {str(e)}")
        return {"success": False, "message": f"保存配置失败: {str(e)}"}

# 测试下载器连接 - 支持通过ID或配置测试
@router.post("/test-client-connection")
async def test_client_connection(
    request: Request,
    torrent_client_manager: TorrentClientManager = Depends(get_torrent_client_manager)
):
    """测试下载器连接"""
    try:
        data = await request.json()
        client_id = data.get("client_id")
        client_config = data.get("client_config")
        
        if client_id:
            # 通过客户端ID测试已配置的客户端
            result = torrent_client_manager.test_client_connection(client_id)
        elif client_config:
            # 通过临时配置测试连接
            result = torrent_client_manager.test_client_connection_by_config(client_config)
        else:
            return {"success": False, "message": "请提供 client_id 或 client_config"}
        
        return result
        
    except Exception as e:
        logger.error(f"测试下载器连接失败: {str(e)}")
        return {"success": False, "message": f"测试连接失败: {str(e)}"}

# 兼容旧版API
@router.post("/save-clients-config")
async def save_clients_config_route(
    clients_config: dict,
    config: Dict[str, Any] = Depends(get_config)
):
    """保存下载器配置（兼容旧版API）"""
    logger.info("收到旧版本下载器配置保存请求，正在转换...")
    try:
        # 将旧格式转换为新格式
        converted_clients = []
        
        for client_type, client_config in clients_config.items():
            if client_type in ["qbittorrent", "transmission"]:
                # 生成唯一ID
                client_id = f"{client_type}_{int(time.time())}"
                converted_clients.append({
                    "id": client_id,
                    "name": f"{client_type.capitalize()} 默认",
                    "type": client_type,
                    **client_config
                })
        
        # 调用新版API
        return await save_torrent_clients(
            {"clients": converted_clients},
            config
        )
        
    except Exception as e:
        logger.error(f"保存下载器配置失败: {str(e)}")
        return {"success": False, "message": f"保存配置失败: {str(e)}"}

# 删除下载器客户端
@router.delete("/torrent-clients/{client_id}")
async def delete_torrent_client(
    client_id: str,
    config: Dict[str, Any] = Depends(get_config)
):
    """删除指定的下载器客户端"""
    try:
        clients_config = config.get("torrent_clients", [])
        
        # 查找并删除指定客户端
        updated_clients = [client for client in clients_config if client.get("id") != client_id]
        
        if len(updated_clients) == len(clients_config):
            return {"success": False, "message": f"未找到客户端: {client_id}"}
        
        # 更新配置
        config["torrent_clients"] = updated_clients
        
        # 保存配置到文件
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        # 更新 TorrentClientManager
        torrent_client_manager = get_torrent_client_manager()
        torrent_client_manager.update_config(config)
        
        logger.info(f"已删除下载器客户端: {client_id}")
        return {"success": True, "message": "客户端已删除"}
        
    except Exception as e:
        logger.error(f"删除下载器客户端失败: {str(e)}")
        return {"success": False, "message": f"删除客户端失败: {str(e)}"}

# 获取支持的客户端类型
@router.get("/torrent-client-types")
async def get_torrent_client_types():
    """获取支持的下载器客户端类型"""
    return {
        "success": True,
        "types": [
            {
                "type": "qbittorrent",
                "name": "qBittorrent",
                "default_port": 8080,
                "fields": ["host", "port", "username", "password", "use_https"]
            },
            {
                "type": "transmission",
                "name": "Transmission",
                "default_port": 9091,
                "fields": ["host", "port", "username", "password", "use_https", "path"]
            }
        ]
    }

# ===== 通知配置API =====

@router.get("/notify/config")
async def get_notify_config():
    """获取通知配置（从文件读取最新config）"""
    config = get_config()
    notify_cfg = config.get("notify", {})
    return {"success": True, "notify": notify_cfg}


@router.post("/notify/config")
async def save_notify_config(payload: Dict[str, Any]):
    """保存通知配置到config.yaml，并保持其余配置不变"""
    try:
        config = get_config()
        new_notify = payload.get("notify", {})
        if not isinstance(new_notify, dict):
            return {"success": False, "message": "无效的通知配置"}

        config["notify"] = new_notify

        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

        _sync_main_config(config)

        logger.info("通知配置已保存")
        return {"success": True, "message": "通知配置已保存"}
    except Exception as e:
        logger.error(f"保存通知配置失败: {str(e)}")
        return {"success": False, "message": f"保存通知配置失败: {str(e)}"}


@router.post("/notify/test")
async def test_notify(payload: Dict[str, Any]):
    """测试发送通知：可携带title/content与临时覆盖的channels"""
    try:
        title = payload.get("title") or "通知测试"
        content = payload.get("content") or "这是一条测试消息"
        channels_override = payload.get("channels") or {}

        config = get_config()
        notify_cfg = copy.deepcopy(config.get("notify", {}))
        enable = notify_cfg.get("enable", True)
        if not enable:
            return {"success": False, "message": "通知功能未启用"}

        channels = notify_cfg.get("channels", {}) or {}
        per_channel_payloads: list[Dict[str, Any]] = []

        use_saved_channels = True

        if isinstance(channels_override, dict) and channels_override:
            use_saved_channels = False
            contains_nested = any(isinstance(val, dict) for val in channels_override.values())
            if contains_nested:
                for _, ch_conf in channels_override.items():
                    if isinstance(ch_conf, dict) and ch_conf.get("enable", True):
                        flat_config = _flatten_notify_channel(ch_conf, notify_cfg)
                        channel_type = ch_conf.get("type", "").lower()
                        if channel_type:
                            flat_config[f"ENABLE_{channel_type.upper()}"] = ch_conf.get("enable", False)
                        per_channel_payloads.append(flat_config)
            else:
                tmp_flat = dict(channels_override)
                if "HITOKOTO" in tmp_flat and isinstance(tmp_flat["HITOKOTO"], bool):
                    tmp_flat["HITOKOTO"] = "true" if tmp_flat["HITOKOTO"] else "false"
                elif "HITOKOTO" not in tmp_flat:
                    tmp_flat["HITOKOTO"] = "true" if bool(notify_cfg.get("hitokoto", True)) else "false"
                per_channel_payloads.append(tmp_flat)

        if use_saved_channels and isinstance(channels, dict):
            for _, ch_conf in channels.items():
                if isinstance(ch_conf, dict) and ch_conf.get("enable"):
                    flat_config = _flatten_notify_channel(ch_conf, notify_cfg)
                    channel_type = ch_conf.get("type", "").lower()
                    if channel_type:
                        flat_config[f"ENABLE_{channel_type.upper()}"] = ch_conf.get("enable", False)
                    per_channel_payloads.append(flat_config)

        valid_payloads: list[Dict[str, Any]] = []
        for flat in per_channel_payloads:
            if _is_valid_notify_payload(flat, TEST_NOTIFY_MINIMAL_KEYS_SETS):
                valid_payloads.append(flat)

        if not valid_payloads:
            return {"success": False, "message": "未检测到可用的通知渠道，请检查渠道是否启用且配置完整"}

        skip_titles = notify_cfg.get("skip_titles", []) or []
        if title in skip_titles:
            return {"success": True, "message": "标题在跳过列表中，未发送"}

        for flat in valid_payloads:
            notify_module.send(title, content, ignore_default_config=True, **flat)
        return {"success": True, "message": "测试通知请求已发出，请检查渠道接收情况"}
    except Exception as e:
        logger.error(f"测试通知发送失败: {str(e)}", exc_info=True)
        return {"success": False, "message": f"测试通知失败: {str(e)}"}

# 从下载器导入Tracker
@router.post("/import-trackers-from-clients")
async def import_trackers_from_clients_route(
    background_tasks: BackgroundTasks,
    hosts_manager: HostsManager = Depends(get_hosts_manager),
    config: Dict[str, Any] = Depends(get_config)
):
    """从所有已启用的下载器客户端导入Tracker"""
    logger.info("开始从下载器客户端导入Tracker")
    try:
        torrent_client_manager = get_torrent_client_manager()
        result = torrent_client_manager.import_trackers_from_clients()
        logger.info(f"导入结果: {result}")
        
        if result.get("status") == "success" and result.get("all_domains"):
            existing_domains = {tracker['domain'] for tracker in config.get('trackers', [])}
            new_trackers_added = False
            cf_domains = []
            non_cf_domains = []
            
            hosts_manager_logger = logging.getLogger('app.services.hosts_manager')
            original_level = hosts_manager_logger.level
            hosts_manager_logger.setLevel(logging.DEBUG)

            for domain in result["all_domains"]:
                d = re.sub(r"^https?://", "", domain, flags=re.IGNORECASE)
                d = d.split("/")[0]
                domain = d

                clean_domain = domain.split(':')[0] if ':' in domain else domain

                logger.info(f"[Cloudflare检测] 正在检测下载器导入的域名: {clean_domain}")
                if hosts_manager.is_cloudflare_domain(clean_domain):
                    cf_domains.append(domain)
                    if domain not in existing_domains:
                        default_ip = DEFAULT_CLOUDFLARE_IP
                        new_tracker = {
                            "name": domain,
                            "domain": domain,
                            "enable": True,
                            "ip": default_ip
                        }
                        config.setdefault('trackers', []).append(new_tracker)
                        existing_domains.add(domain)
                        new_trackers_added = True
                else:
                    logger.info(f"[Cloudflare检测] 域名 {clean_domain} 不是Cloudflare域名，已跳过")
                    non_cf_domains.append(domain)

            hosts_manager_logger.setLevel(original_level)

            if cf_domains:
                logger.info("=== Cloudflare站点检测结果 ===")
                logger.info(f"成功检测到 {len(cf_domains)} 个Cloudflare站点:")
                for domain in cf_domains:
                    logger.info(f"- {domain}")
            
            if non_cf_domains:
                logger.info(f"检测到 {len(non_cf_domains)} 个非Cloudflare站点:")
                for domain in non_cf_domains:
                    logger.info(f"- {domain}")

            if new_trackers_added:
                with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                logger.info("已更新配置文件，添加了新的Tracker")
                hosts_manager.update_config(config)
                _sync_main_config(config, "同步刷新全局config对象，确保前端获取到最新tracker列表", "刷新全局config对象失败")
                background_tasks.add_task(hosts_manager.update_hosts)

                cf_only_message = f"成功导入 {len(cf_domains)} 个Cloudflare站点"
                if non_cf_domains:
                    cf_only_message += f"，已过滤 {len(non_cf_domains)} 个非Cloudflare站点"
                result["message"] = cf_only_message + "，Hosts更新任务已在后台启动"
            else:
                if cf_domains:
                    result["message"] = f"未发现新的Cloudflare站点，已有站点 {len(cf_domains)} 个，过滤非Cloudflare站点 {len(non_cf_domains)} 个"
                else:
                    result["message"] = f"未找到任何Cloudflare站点，已过滤非Cloudflare站点 {len(non_cf_domains)} 个"

            client_summary = []
            for _, client_result in result.get("client_results", {}).items():
                if client_result.get("success"):
                    client_summary.append(f"{client_result['name']}: {client_result['count']}个")
                else:
                    client_summary.append(f"{client_result['name']}: 失败({client_result.get('error', '未知错误')})")
            
            if client_summary:
                result["client_summary"] = "；".join(client_summary)
        
        return result
        
    except Exception as e:
        logger.error(f"从下载器客户端导入Tracker失败: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"导入过程中发生错误: {str(e)}"}

@router.post("/clear-and-update-hosts")
async def clear_and_update_hosts(
    background_tasks: BackgroundTasks,
    hosts_manager: HostsManager = Depends(get_hosts_manager)
):
    """清理项目分区并重新生成hosts内容（保留原有系统hosts未受影响）"""
    try:
        hosts_manager.clear_project_sections()
        def task():
            ok = hosts_manager.update_hosts()
            status = hosts_manager.get_task_status() if hasattr(hosts_manager, 'get_task_status') else {}
            msg = status.get('message') if isinstance(status, dict) else ("更新完成" if ok else "更新失败")
            logger.info(f"[任务通知] 清空并更新Hosts -> {msg}")
            _send_task_notify("清空并更新Hosts", msg)
        background_tasks.add_task(task)
        return {"message": "已清理项目分区并启动更新任务（原有hosts内容已保留）"}
    except Exception as e:
        logger.error(f"清空并更新hosts失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清空并更新hosts失败: {str(e)}")

@router.post("/clear-all-trackers")
async def clear_all_trackers(
    background_tasks: BackgroundTasks,
    hosts_manager: HostsManager = Depends(get_hosts_manager)
):
    """清空所有tracker并同步更新hosts"""
    try:
        config = get_config()
        config["trackers"] = []
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        hosts_manager.update_config(config)
        _sync_main_config(config)
        background_tasks.add_task(hosts_manager.update_hosts)
        return {"message": "已清空所有tracker并同步更新hosts"}
    except Exception as e:
        logger.error(f"清空所有tracker失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清空所有tracker失败: {str(e)}")


# 保存系统hosts内容
@router.post("/save-hosts-content")
async def save_hosts_content(
    payload: Dict[str, Any],
    background_tasks: BackgroundTasks,
    hosts_manager: HostsManager = Depends(get_hosts_manager)
):
    try:
        content = payload.get("content", "")
        if not isinstance(content, str):
            raise HTTPException(status_code=400, detail="无效的内容")
        hosts_path = hosts_manager._get_hosts_path()
        with open(hosts_path, 'w') as f:
            f.write(content)
        background_tasks.add_task(hosts_manager.update_hosts)
        return {"success": True, "message": "Hosts已保存，已启动后台更新"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存hosts失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存hosts失败: {str(e)}")

# 测试通知渠道
@router.post("/notify/test/{channel_key}")
async def test_notify_channel(
    channel_key: str,
    background_tasks: BackgroundTasks
):
    """测试指定通知渠道"""
    try:
        config = get_config()
        notify_cfg = config.get("notify", {})
        channels = notify_cfg.get("channels", {})
        
        if channel_key not in channels:
            raise HTTPException(status_code=404, detail="通知渠道不存在")
            
        channel_config = channels[channel_key]
        
        title = "🔔 PT-Accelerator测试通知："
        content = f"这是一条来自 【{channel_config.get('name', channel_key)}】通知渠道 的测试消息！\n发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        flat_config = {}
        for k, v in channel_config.items():
            if k not in ("name", "type", "enable"):
                flat_config[k] = v

        def send_test():
            try:
                flat_config[f"ENABLE_{channel_config.get('type', '').upper()}"] = True
                notify_module.send(title, content, ignore_default_config=True, **flat_config)
            except Exception as e:
                logger.error(f"测试通知发送失败: {e}")

        background_tasks.add_task(send_test)
        
        return {"message": "测试消息已发送"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"测试通知失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试通知失败: {str(e)}")

@router.get("/version")
async def version():
    """获取当前系统版本号"""
    return {"version": get_version()}
