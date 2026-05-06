"""
Slack 通知渠道
"""
import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


class SlackChannel:
    """Slack Webhook 通知"""

    def __init__(self, config: dict):
        self._webhook_url = str(config.get("SLACK_WEBHOOK_URL") or config.get("webhook_url") or "").strip()

    def send(self, title: str, message: str) -> bool:
        if not self._webhook_url:
            logger.warning("Slack 渠道未配置")
            return False

        payload = {"text": f"{title}\n\n{message}"}

        try:
            with httpx.Client(timeout=15) as client:
                response = client.post(self._webhook_url, json=payload)
                if response.is_success:
                    logger.info(f"Slack 通知发送成功，标题：{title}")
                    return True
                logger.error(f"Slack 通知发送失败，状态码：{response.status_code}，响应：{response.text}")
        except Exception as e:
            logger.error(f"Slack 通知发送异常：{e}")
        return False
