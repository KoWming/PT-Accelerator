"""
Server酱通知渠道
"""
import re

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ServerJChannel:
    """Server酱通知"""

    def __init__(self, config: dict):
        self._push_key = str(config.get("PUSH_KEY") or "").strip()

    def send(self, title: str, message: str) -> bool:
        if not self._push_key:
            logger.warning("Server酱渠道未配置")
            return False

        match = re.match(r"sctp(\d+)t", self._push_key)
        if match:
            url = f"https://{match.group(1)}.push.ft07.com/send/{self._push_key}.send"
        else:
            url = f"https://sctapi.ftqq.com/{self._push_key}.send"

        payload = {
            "text": title,
            "desp": message.replace("\n", "\n\n"),
        }

        try:
            with httpx.Client(timeout=15) as client:
                response = client.post(url, data=payload)
                data = response.json() if response.content else {}
                if response.is_success and (data.get("errno") == 0 or data.get("code") == 0):
                    logger.info(f"Server酱通知发送成功，标题：{title}")
                    return True
                logger.error(f"Server酱通知发送失败，状态码：{response.status_code}，响应：{response.text}")
        except Exception as e:
            logger.error(f"Server酱通知发送异常：{e}")
        return False
