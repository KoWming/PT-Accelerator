"""
iGot 通知渠道
"""
import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


class IgotChannel:
    """iGot 聚合推送"""

    def __init__(self, config: dict):
        self._push_key = str(config.get("IGOT_PUSH_KEY") or "").strip()

    def send(self, title: str, message: str) -> bool:
        if not self._push_key:
            logger.warning("iGot 渠道未配置")
            return False

        url = f"https://push.hellyw.com/{self._push_key}"
        payload = {"title": title, "content": message}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            with httpx.Client(timeout=15) as client:
                response = client.post(url, data=payload, headers=headers)
                data = response.json() if response.content else {}
                if response.is_success and data.get("ret") == 0:
                    logger.info(f"iGot 通知发送成功，标题：{title}")
                    return True
                logger.error(f"iGot 通知发送失败，状态码：{response.status_code}，响应：{response.text}")
        except Exception as e:
            logger.error(f"iGot 通知发送异常：{e}")
        return False
