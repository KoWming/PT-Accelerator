"""
备份管线：创建备份 → 上传到 WebDAV → 发送通知

BackupService 公共 API:
  - create_backup(description) -> {"backup_id", "file_path", "message"}
  - upload_to_webdav(backup_id) -> {"success": bool, "message": str}
  - list_backups() -> list[dict]
"""
import asyncio
import threading
from datetime import datetime

from app.services.backup_service import backup_service
from app.services.notify_service import build_structured_notification, notify_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BackupPipeline:
    """备份管线"""

    def run(self) -> dict:
        """
        执行完整备份管线
        1. 创建本地备份
        2. 上传到 WebDAV
        3. 发送通知
        """
        logger.info("=== 备份管线开始 ===")
        result = {
            "success": True,
            "backup_id": "",
            "file_path": "",
            "uploaded": False,
            "errors": [],
        }

        try:
            # Step 1: 创建本地备份
            backup_result = backup_service.create_backup(description="定时备份")
            result["backup_id"] = backup_result.get("backup_id", "")
            result["file_path"] = backup_result.get("file_path", "")
            logger.info(f"本地备份已创建：{result['file_path']}")

            # Step 2: 上传到 WebDAV（在独立线程中安全执行异步方法）
            upload_result = {}

            def _upload_target():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    upload_result["value"] = loop.run_until_complete(
                        backup_service.upload_to_webdav(result["backup_id"])
                    )
                finally:
                    loop.close()

            t = threading.Thread(target=_upload_target, daemon=True)
            t.start()
            t.join()
            upload_result = upload_result.get("value", {})
            result["uploaded"] = upload_result.get("success", False)
            if not result["uploaded"]:
                logger.warning(f"WebDAV 上传失败：{upload_result.get('message', '')}")
            else:
                logger.info("备份已上传到 WebDAV")

            # Step 3: 发送通知
            self._send_notification(result)

        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
            logger.error(f"备份管线异常：{e}")

        logger.info("=== 备份管线完成 ===")
        return result

    def _send_notification(self, result: dict):
        """发送备份完成通知"""
        try:
            if result["uploaded"]:
                status = "已上传到 WebDAV"
            elif result["success"]:
                status = "已本地打包"
            else:
                status = "备份失败"

            title, message = build_structured_notification(
                header="备份任务",
                task_type="备份任务",
                success=bool(result.get("success", False)),
                detail_title="备份结果",
                detail_items=[
                    ("备份 ID", result.get("backup_id") or "未知"),
                    ("备份文件", result.get("file_path") or "未知"),
                    ("备份状态", status),
                ],
                result_text="任务完成" if result.get("success") else "任务失败",
                push_time=datetime.now(),
            )

            notify_service.send(
                channel_id="default",
                title=title,
                message=message,
            )
        except Exception as e:
            logger.warning(f"发送通知失败：{e}")
