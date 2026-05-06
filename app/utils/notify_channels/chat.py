"""
Synology Chat 通知渠道
"""
import json

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChatChannel:
    """Synology Chat 通知"""

    def __init__(self, config: dict):
        self._url = str(config.get("CHAT_URL") or "").strip()
        self._token = str(config.get("CHAT_TOKEN") or "").strip()

    def send(self, title: str, message: str) -> bool:
        if not self._url or not self._token:
            logger.warning("Synology Chat 渠道未配置")
            return False

        payload = "payload=" + json.dumps({"text": f"{title}\n{message}"}, ensure_ascii=False)
        url = f"{self._url}{self._token}"

        try:
            with httpx.Client(timeout=15) as client:
                response = client.post(url, content=payload.encode("utf-8"))
                if response.is_success:
                    logger.info(f"Synology Chat 通知发送成功，标题：{title}")
                    return True
                logger.error(f"Synology Chat 通知发送失败，状态码：{response.status_code}，响应：{response.text}")
        except Exception as e:
            logger.error(f"Synology Chat 通知发送异常：{e}")
        return False
