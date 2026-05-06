"""
Bark 通知渠道
"""
import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


class BarkChannel:
    """Bark 通知"""

    FIELD_MAP = {
        "BARK_ARCHIVE": "isArchive",
        "BARK_GROUP": "group",
        "BARK_SOUND": "sound",
        "BARK_ICON": "icon",
        "BARK_LEVEL": "level",
        "BARK_URL": "url",
    }

    def __init__(self, config: dict):
        self._push = str(config.get("BARK_PUSH") or config.get("device_key") or config.get("server_url") or "").strip()
        self._config = config or {}

    def send(self, title: str, message: str) -> bool:
        if not self._push:
            logger.warning("Bark 渠道未配置")
            return False

        url = self._push if self._push.startswith("http") else f"https://api.day.app/{self._push}"
        payload = {
            "title": title,
            "body": message,
        }
        for source_key, target_key in self.FIELD_MAP.items():
            value = self._config.get(source_key)
            if value not in (None, ""):
                payload[target_key] = value

        try:
            with httpx.Client(timeout=15) as client:
                response = client.post(url, json=payload)
                data = response.json() if response.content else {}
                if response.is_success and data.get("code") == 200:
                    logger.info(f"Bark 通知发送成功，标题：{title}")
                    return True
                logger.error(f"Bark 通知发送失败，状态码：{response.status_code}，响应：{response.text}")
        except Exception as e:
            logger.error(f"Bark 通知发送异常：{e}")
        return False
