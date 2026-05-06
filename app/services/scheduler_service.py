"""
APScheduler 调度服务封装：任务注册 / 启停 / 管理

支持的任务类型：
    - cfst:    CFST 测速任务
    - hosts:   Hosts 更新任务
    - backup:  备份任务
"""
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from app.config import config
from app.services.tracker_service import tracker_service
from app.utils.logger import get_logger



logger = get_logger(__name__)

# APScheduler 实例
scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

# Pipeline 函数占位（延迟导入避免循环依赖）
_pipeline_funcs: dict = {}


def _get_pipeline_func(job_id: str):
    """获取 Pipeline 执行函数（延迟加载）"""
    if job_id not in _pipeline_funcs:
        if job_id == "cfst":
            from app.pipelines.cfst_pipeline import CfstPipeline

            def _run_cfst():
                trackers = [
                    t.get("url", "")
                    for t in tracker_service.list_enabled_cloudflare()
                    if t.get("url")
                ]

                if not trackers:
                    logger.warning("CFST 调度任务跳过：未配置任何已启用的 Cloudflare Tracker")
                    return None
                pipeline = CfstPipeline()
                return pipeline.run(trackers=trackers)


            _pipeline_funcs[job_id] = _run_cfst
        elif job_id == "hosts":
            from app.pipelines.hosts_pipeline import HostsPipeline
            from app.services.hosts_service import HostsService
            from app.services.cfst_service import cfst_service
            def _run_hosts():
                import asyncio
                svc = HostsService()
                sources = svc.list_sources()
                if not sources:
                    logger.warning("Hosts 调度任务跳过：未配置任何 hosts 源")
                    return
                cf_ip_map = cfst_service.get_cached_results()
                if not cf_ip_map:
                    logger.warning("Hosts 调度任务跳过：无可用的 CFST IP 数据")
                    return
                pipeline = HostsPipeline()
                asyncio.run(pipeline.run(sources=sources, cf_ip_map=cf_ip_map))
            _pipeline_funcs[job_id] = _run_hosts
        elif job_id == "backup":
            from app.pipelines.backup_pipeline import BackupPipeline
            def _run_backup():
                pipeline = BackupPipeline()
                # BackupPipeline.run() 返回结果
                return pipeline.run()
            _pipeline_funcs[job_id] = _run_backup
        else:
            raise ValueError(f"不支持的任务类型: {job_id}")
    return _pipeline_funcs[job_id]


def _validate_job_id(job_id: str) -> bool:
    """验证任务ID是否有效"""
    return job_id in ["cfst", "hosts", "backup"]


def _validate_trigger(trigger: str, interval_seconds: int, cron_expr: Optional[str]) -> tuple:
    """
    验证触发器参数

    Returns:
        (trigger_type, trigger_obj)
    Raises:
        ValueError: 参数无效
    """
    if trigger == "interval":
        if interval_seconds < 60:
            raise ValueError("间隔时间不能少于 60 秒")
        if interval_seconds > 604800:
            raise ValueError("间隔时间不能超过 604800 秒（7天）")
        return ("interval", IntervalTrigger(seconds=interval_seconds))

    elif trigger == "cron":
        if not cron_expr:
            raise ValueError("Cron 模式必须提供 cron_expr 参数")
        # 解析 cron_expr: "分 时 日 月 周"
        fields = cron_expr.strip().split()
        if len(fields) < 5:
            raise ValueError("Cron 表达式格式错误，应为：分 时 日 月 周")
        return ("cron", CronTrigger(
            minute=fields[0],
            hour=fields[1],
            day=fields[2],
            month=fields[3],
            day_of_week=fields[4],
        ))

    else:
        raise ValueError(f"不支持的触发类型: {trigger}，支持：interval | cron")


def _load_jobs_from_config() -> list[dict]:
    """从配置加载任务列表"""
    jobs = []
    for job_id in ["cfst", "hosts", "backup"]:
        job_cfg = config.get(f"scheduler.jobs.{job_id}", default={})
        if job_cfg:
            jobs.append({
                "job_id": job_id,
                "name": job_cfg.get("name", job_id.upper()),
                "trigger": job_cfg.get("trigger", "interval"),
                "enabled": job_cfg.get("enabled", False),
                "interval_seconds": job_cfg.get("interval_seconds", 3600),
                "cron_expr": job_cfg.get("cron_expr"),
            })
    return jobs


def _save_job_to_config(job_id: str, name: str, trigger: str, enabled: bool,
                        interval_seconds: int, cron_expr: Optional[str]):
    """保存任务配置到 config"""
    job_cfg = {
        "name": name,
        "trigger": trigger,
        "enabled": enabled,
        "interval_seconds": interval_seconds,
        "cron_expr": cron_expr,
    }
    config.set(f"scheduler.jobs.{job_id}", job_cfg)
    config.save()


def list_jobs() -> list[dict]:
    """
    获取所有调度任务列表

    Returns:
        任务配置列表，包含 APScheduler 任务状态
    """
    jobs = _load_jobs_from_config()
    result = []

    for job in jobs:
        job_id = job["job_id"]
        ap_job = scheduler.get_job(job_id)
        job_data = {
            "job_id": job_id,
            "name": job["name"],
            "trigger": job["trigger"],
            "enabled": job["enabled"],
            "interval_seconds": job["interval_seconds"],
            "cron_expr": job["cron_expr"],
            "status": _get_job_status(ap_job),
            "next_run": _get_job_next_run(ap_job),
            "last_run": None,  # APScheduler 不直接暴露上次运行时间
        }
        result.append(job_data)

    return result


def _get_job_status(ap_job) -> str:
    """获取任务运行状态"""
    if not ap_job:
        return "idle"
    try:
        next_run = ap_job.next_run_time
        return "scheduled" if next_run else "idle"
    except Exception:
        return "idle"


def _get_job_next_run(ap_job) -> Optional[str]:
    """获取任务下次运行时间"""
    if not ap_job:
        return None
    try:
        next_run = ap_job.next_run_time
        return next_run.isoformat() if next_run else None
    except Exception:
        return None


def get_job(job_id: str) -> Optional[dict]:
    """获取单个任务配置"""
    if not _validate_job_id(job_id):
        return None

    job_cfg = config.get(f"scheduler.jobs.{job_id}", default=None)
    if not job_cfg:
        return None

    ap_job = scheduler.get_job(job_id)
    return {
        "job_id": job_id,
        "name": job_cfg.get("name", job_id.upper()),
        "trigger": job_cfg.get("trigger", "interval"),
        "enabled": job_cfg.get("enabled", False),
        "interval_seconds": job_cfg.get("interval_seconds", 3600),
        "cron_expr": job_cfg.get("cron_expr"),
        "status": _get_job_status(ap_job),
        "next_run": _get_job_next_run(ap_job),
    }


def add_job(
    job_id: str,
    name: str,
    trigger: str = "interval",
    enabled: bool = True,
    interval_seconds: int = 3600,
    cron_expr: Optional[str] = None,
) -> dict:
    """
    添加/更新调度任务

    Args:
        job_id: 任务ID（cfst | hosts | backup）
        name: 任务名称
        trigger: 触发类型（interval | cron）
        enabled: 是否启用
        interval_seconds: 间隔秒数（trigger=interval 时）
        cron_expr: Cron 表达式（trigger=cron 时）

    Returns:
        任务配置
    """
    if not _validate_job_id(job_id):
        raise ValueError(f"不支持的任务ID: {job_id}，支持：cfst | hosts | backup")

    # 验证触发器
    _validate_trigger(trigger, interval_seconds, cron_expr)

    # 保存配置
    _save_job_to_config(job_id, name, trigger, enabled, interval_seconds, cron_expr)

    # 从调度器移除旧任务（如果存在）
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass

    # 如果启用，注册到调度器
    if enabled:
        func = _get_pipeline_func(job_id)
        _, trigger_obj = _validate_trigger(trigger, interval_seconds, cron_expr)
        scheduler.add_job(func, trigger_obj, id=job_id, replace_existing=True)
        logger.info(f"调度任务已添加: {job_id} ({trigger})")
    else:
        logger.info(f"调度任务配置已保存（未启用）: {job_id}")

    result = get_job(job_id)
    if result is None:
        raise RuntimeError(f"添加任务后无法获取配置: {job_id}")
    return result


def remove_job(job_id: str) -> bool:
    """
    删除调度任务

    Returns:
        是否成功删除
    """
    if not _validate_job_id(job_id):
        return False

    # 从调度器移除
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass

    # 删除配置
    config.set(f"scheduler.jobs.{job_id}", None)
    config.save()

    logger.info(f"调度任务已删除: {job_id}")
    return True


def enable_job(job_id: str) -> Optional[dict]:
    """
    启用调度任务

    Returns:
        更新后的任务配置，失败返回 None
    """
    if not _validate_job_id(job_id):
        return None

    job = get_job(job_id)
    if not job:
        return None

    # 重新注册
    func = _get_pipeline_func(job_id)
    _, trigger_obj = _validate_trigger(
        job["trigger"], job["interval_seconds"], job["cron_expr"]
    )
    scheduler.add_job(func, trigger_obj, id=job_id, replace_existing=True)

    # 更新配置
    config.set(f"scheduler.jobs.{job_id}.enabled", True)
    config.save()

    logger.info(f"调度任务已启用: {job_id}")
    return get_job(job_id)


def disable_job(job_id: str) -> Optional[dict]:
    """
    禁用调度任务（从调度器移除，保留配置）

    Returns:
        更新后的任务配置，失败返回 None
    """
    if not _validate_job_id(job_id):
        return None

    job = get_job(job_id)
    if not job:
        return None

    # 从调度器移除
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass

    # 更新配置
    config.set(f"scheduler.jobs.{job_id}.enabled", False)
    config.save()

    logger.info(f"调度任务已禁用: {job_id}")
    return get_job(job_id)


def trigger_job(job_id: str) -> bool:
    """
    手动触发任务执行（立即执行一次）

    Returns:
        是否成功触发
    """
    if not _validate_job_id(job_id):
        return False

    try:
        func = _get_pipeline_func(job_id)
        # 使用 modify() 立即触发一次
        job = scheduler.get_job(job_id)
        if job:
            job.modify(next_run_time=datetime.now())
        else:
            # 任务不在调度器中，直接调用函数
            logger.info(f"手动触发任务（未在调度器中）: {job_id}")
            # 在后台线程执行
            import threading
            threading.Thread(target=func, daemon=True).start()
        return True
    except Exception as e:
        logger.error(f"触发任务失败 {job_id}: {e}")
        return False


def start_scheduler():
    """启动调度器"""
    if not scheduler.running:
        scheduler.start()
        logger.info("调度器已启动")

        # 注册所有已启用的任务
        for job in _load_jobs_from_config():
            if job["enabled"]:
                try:
                    func = _get_pipeline_func(job["job_id"])
                    _, trigger_obj = _validate_trigger(
                        job["trigger"], job["interval_seconds"], job["cron_expr"]
                    )
                    scheduler.add_job(func, trigger_obj, id=job["job_id"], replace_existing=True)
                    logger.info(f"已注册任务到调度器: {job['job_id']}")
                except Exception as e:
                    logger.error(f"注册任务失败 {job['job_id']}: {e}")


def shutdown_scheduler():
    """关闭调度器"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("调度器已关闭")
