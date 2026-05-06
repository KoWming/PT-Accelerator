"""
钉钉通知渠道
"""
import base64
import hashlib
import hmac
import time
import urllib.parse

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


class DingTalkChannel:
    """钉钉机器人通知"""

    def __init__(self, config: dict):
        self._token = str(config.get("DD_BOT_TOKEN") or "").strip()
        self._secret = str(config.get("DD_BOT_SECRET") or "").strip()

    def send(self, title: str, message: str) -> bool:
        if not self._token or not self._secret:
            logger.warning("钉钉渠道未配置")
            return False

        timestamp = str(round(time.time() * 1000))
        string_to_sign = f"{timestamp}\n{self._secret}"
        sign = urllib.parse.quote_plus(
            base64.b64encode(
                hmac.new(self._secret.encode("utf-8"), string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
            )
        )
        url = f"https://oapi.dingtalk.com/robot/send?access_token={self._token}&timestamp={timestamp}&sign={sign}"
        payload = {"msgtype": "text", "text": {"content": f"{title}\n\n{message}"}}

        try:
            with httpx.Client(timeout=15) as client:
                response = client.post(url, json=payload)
                data = response.json() if response.content else {}
                if response.is_success and data.get("errcode") == 0:
                    logger.info(f"钉钉通知发送成功，标题：{title}")
                    return True
                logger.error(f"钉钉通知发送失败，状态码：{response.status_code}，响应：{response.text}")
        except Exception as e:
            logger.error(f"钉钉通知发送异常：{e}")
        return False
