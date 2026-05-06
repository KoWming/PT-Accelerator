"""
企业微信通知渠道
"""
import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


class WecomChannel:
    """企业微信机器人通知"""

    def __init__(self, config: dict):
        self._key = str(config.get("QYWX_KEY") or config.get("webhook_url") or "").strip()
        self._origin = str(config.get("QYWX_ORIGIN") or "https://qyapi.weixin.qq.com").rstrip("/")

    def send(self, title: str, message: str) -> bool:
        if not self._key:
            logger.warning("企业微信渠道未配置")
            return False

        url = self._key if self._key.startswith("http") else f"{self._origin}/cgi-bin/webhook/send?key={self._key}"
        payload = {"msgtype": "text", "text": {"content": f"{title}\n\n{message}"}}

        try:
            with httpx.Client(timeout=15) as client:
                response = client.post(url, json=payload)
                data = response.json() if response.content else {}
                if response.is_success and data.get("errcode") == 0:
                    logger.info(f"企业微信通知发送成功，标题：{title}")
                    return True
                logger.error(f"企业微信通知发送失败，状态码：{response.status_code}，响应：{response.text}")
        except Exception as e:
            logger.error(f"企业微信通知发送异常：{e}")
        return False
