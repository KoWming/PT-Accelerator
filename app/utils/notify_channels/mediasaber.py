"""
Media Saber 通知渠道
"""
import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


class MediaSaberChannel:
    """Media Saber 通知"""

    def __init__(self, config: dict):
        self._host = str(config.get("MEDIASABER_HOST") or "").strip().rstrip("/")
        self._api_key = str(config.get("MEDIASABER_APIKEY") or "").strip()

    def send(self, title: str, message: str) -> bool:
        if not self._host or not self._api_key:
            logger.warning("Media Saber 渠道未配置")
            return False

        url = f"{self._host}/api/v1/message/openSend"
        headers = {
            "Content-Type": "application/json",
            "apiKey": self._api_key,
        }
        payload = {
            "title": title,
            "content": message,
        }

        try:
            with httpx.Client(timeout=15) as client:
                response = client.post(url, json=payload, headers=headers)
                if response.is_success:
                    logger.info(f"Media Saber 通知发送成功，标题：{title}")
                    return True
                logger.error(f"Media Saber 通知发送失败，状态码：{response.status_code}，响应：{response.text}")
        except Exception as e:
            logger.error(f"Media Saber 通知发送异常：{e}")
        return False
