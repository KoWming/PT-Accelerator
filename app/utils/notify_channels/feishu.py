"""
飞书通知渠道
"""
import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


class FeishuChannel:
    """飞书机器人通知"""

    def __init__(self, config: dict):
        self._key = str(config.get("FSKEY") or "").strip()

    def send(self, title: str, message: str) -> bool:
        if not self._key:
            logger.warning("飞书渠道未配置")
            return False

        url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{self._key}"
        payload = {"msg_type": "text", "content": {"text": f"{title}\n\n{message}"}}

        try:
            with httpx.Client(timeout=15) as client:
                response = client.post(url, json=payload)
                data = response.json() if response.content else {}
                if response.is_success and data.get("code", data.get("StatusCode", 0)) == 0:
                    logger.info(f"飞书通知发送成功，标题：{title}")
                    return True
                logger.error(f"飞书通知发送失败，状态码：{response.status_code}，响应：{response.text}")
        except Exception as e:
            logger.error(f"飞书通知发送异常：{e}")
        return False
