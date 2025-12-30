import logging
from typing import Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.cloudflare_speed_test import CloudflareSpeedTestService
from app.services.hosts_manager import HostsManager

logger = logging.getLogger(__name__)

class SchedulerService:
    """调度器服务，用于定时执行任务"""
    
    def __init__(self, config: Dict[str, Any], cloudflare_service: CloudflareSpeedTestService, hosts_manager: HostsManager):
        self.config = config
        self.cloudflare_service = cloudflare_service
        self.hosts_manager = hosts_manager
        self.scheduler = None  # 初始化为None，在start时创建
        self._create_scheduler()  # 创建新的调度器
        # 添加任务状态追踪
        self.task_status = {"status": "done", "message": "无任务"}
    
    def _create_scheduler(self):
        """创建一个新的调度器实例"""
        # 防止残留
        if self.scheduler is not None:
            try:
                self.scheduler.shutdown(wait=False)
            except Exception:
                pass
            self.scheduler = None
        # 配置调度器，设置作业执行器选项
        self.scheduler = BackgroundScheduler(
            job_defaults={
                'max_instances': 1,  # 默认最大实例数为1
                'coalesce': True,  # 合并延迟的任务
                'misfire_grace_time': 300  # 错过执行时间后5分钟内仍可执行
            }
        )
        self._setup_jobs()
        logger.info("已创建新的调度器实例")
    
    def update_config(self, config: Dict[str, Any]):
        """更新配置"""
        logger.info("更新调度器配置")
        old_config = self.config
        self.config = config
        
        # 检查CRON是否变更 (Cloudflare 或 Backup)
        old_cf_cron = old_config.get("cloudflare", {}).get("cron", "0 0 * * *")
        new_cf_cron = config.get("cloudflare", {}).get("cron", "0 0 * * *")
        
        old_bk_cron = old_config.get("backup", {}).get("cron", "0 2 * * *")
        new_bk_cron = config.get("backup", {}).get("cron", "0 2 * * *")
        
        # 检查启用状态变更
        old_bk_enable = old_config.get("backup", {}).get("enable", False)
        new_bk_enable = config.get("backup", {}).get("enable", False)

        if (old_cf_cron != new_cf_cron) or (old_bk_cron != new_bk_cron) or (old_bk_enable != new_bk_enable):
            logger.info("定时任务配置变更，需要重启调度器")
            
            # 如果调度器正在运行，需要重启调度器
            if self.is_running():
                self.stop()
                self._create_scheduler()
                self.start()
            else:
                # 调度器未运行，只需要更新任务配置
                self._setup_jobs()
        else:
            # CRON未变更，只需要更新配置
            logger.info("定时任务配置未变更，无需重启调度器")
    
    def _setup_jobs(self):
        """设置定时任务"""
        if not self.scheduler:
            logger.error("调度器实例不存在，无法设置任务")
            return
            
        # 清除现有的所有任务
        if self.scheduler.running:
            logger.info("清除现有的所有定时任务")
            self.scheduler.remove_all_jobs()
        else:
            logger.info("调度器未运行，不需要清除任务")
        
        # 添加合并后的定时任务（IP优选+更新hosts）
        cloudflare_config = self.config.get("cloudflare", {})
        if cloudflare_config.get("enable", True):
            cron_expr = cloudflare_config.get("cron", "0 0 * * *")  # 默认每天0点执行
            logger.info(f"准备添加定时任务，CRON表达式: {cron_expr}")
            
            try:
                # 创建一个组合任务函数
                def combined_task():
                    import time
                    task_start_time = time.time()
                    logger.info("开始执行组合任务：优选IP + 更新hosts源（严格串行）")
                    # 更新任务状态
                    self.task_status = {"status": "running", "message": "正在执行定时IP优选任务"}
                    try:
                        ok, notify_msg = self.hosts_manager.run_cfst_and_update_hosts()
                        status = self.hosts_manager.get_task_status() if hasattr(self.hosts_manager, 'get_task_status') else {}
                        # status['message'] is now the SHORT message
                        short_msg = status.get('message') if isinstance(status, dict) else ("定时IP优选任务完成" if ok else "定时IP优选任务失败")
                        
                        self.task_status = {"status": "done", "message": short_msg}
                        task_duration = time.time() - task_start_time
                        logger.info(f"组合任务完成：优选IP + 更新hosts源（严格串行），耗时 {task_duration:.2f} 秒")
                        
                        # 发送定时任务完成通知 (使用详细消息)
                        try:
                            from app.api.routes import _send_task_notify
                            logger.info(f"[定时任务通知] IP优选与Hosts更新 -> {short_msg}")
                            # 使用返回的详细消息发送pusher通知
                            _send_task_notify("IP优选与Hosts更新", notify_msg)
                        except Exception as notify_e:
                            logger.error(f"发送定时任务通知失败: {str(notify_e)}")
                    except Exception as e:
                        error_msg = f"定时任务失败: {str(e)}"
                        self.task_status = {"status": "done", "message": error_msg}
                        task_duration = time.time() - task_start_time
                        logger.error(f"执行定时任务失败: {str(e)}，耗时 {task_duration:.2f} 秒", exc_info=True)
                        
                        # 发送定时任务失败通知
                        try:
                            from app.api.routes import _send_task_notify
                            logger.info(f"[定时任务通知] IP优选与Hosts更新 -> {error_msg}")
                            _send_task_notify("IP优选与Hosts更新", error_msg)
                        except Exception as notify_e:
                            logger.error(f"发送定时任务失败通知失败: {str(notify_e)}")
                    finally:
                        # 确保任务状态正确结束
                        task_duration = time.time() - task_start_time
                        logger.info(f"定时任务函数执行完毕，总耗时 {task_duration:.2f} 秒")
                
                self.scheduler.add_job(
                    combined_task,
                    CronTrigger.from_crontab(cron_expr),
                    id="combined_cloudflare_and_hosts_task",
                    name="IP优选与Hosts更新定时任务",
                    max_instances=1,  # 确保同一时间只有一个实例运行
                    coalesce=True,  # 如果任务被延迟，合并执行
                    misfire_grace_time=300  # 如果错过执行时间，5分钟内仍可执行
                )
                logger.info(f"已添加组合定时任务(IP优选与Hosts更新)，CRON表达式: {cron_expr}")
            except Exception as e:
                logger.error(f"添加组合定时任务失败: {str(e)}")
        else:
            logger.info("CloudflareSpeedTest优选功能已禁用，不添加相关定时任务")

        # 添加备份定时任务
        backup_config = self.config.get("backup", {})
        if backup_config.get("enable", False):
            cron_expr = backup_config.get("cron", "0 2 * * *")  # 默认每天凌晨2点
            logger.info(f"准备添加备份定时任务，CRON表达式: {cron_expr}")
            
            try:
                def backup_task():
                    logger.info("开始执行定时备份任务")
                    from app.services.backup_service import BackupService
                    backup_service = BackupService()
                    # 重新读取最新配置，确保使用最新凭据
                    from app.api.routes import get_config
                    current_config = get_config()
                    
                    if backup_service.backup_config(current_config):
                        logger.info("定时备份任务完成")
                    else:
                        logger.error("定时备份任务失败")
                
                self.scheduler.add_job(
                    backup_task,
                    CronTrigger.from_crontab(cron_expr),
                    id="backup_config_task",
                    name="配置备份定时任务",
                    max_instances=1,
                    coalesce=True,
                    misfire_grace_time=300
                )
                logger.info(f"已添加备份定时任务，CRON表达式: {cron_expr}")
            except Exception as e:
                logger.error(f"添加备份定时任务失败: {str(e)}")
        else:
            logger.info("备份功能已禁用，不添加备份定时任务")
    
    def start(self):
        """启动调度器"""
        if self.scheduler is None:
            self._create_scheduler()
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("调度器已启动")
    
    def stop(self):
        """停止调度器"""
        if self.scheduler:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
            self.scheduler = None
            logger.info("调度器已停止并清除")
    
    def is_running(self) -> bool:
        """检查调度器是否运行中"""
        return self.scheduler is not None and self.scheduler.running
    
    def get_jobs(self) -> list:
        """获取所有定时任务"""
        jobs = []
        if self.scheduler:
            for job in self.scheduler.get_jobs():
                next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else "未安排"
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": next_run
                })
        return jobs
        
    def get_task_status(self):
        """获取当前任务状态
        
        Returns:
            任务状态字典: 包含status和message
        """
        return self.task_status