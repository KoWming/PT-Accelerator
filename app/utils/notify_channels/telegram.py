"""
Telegram 通知渠道
"""
import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


class TelegramChannel:
    """Telegram Bot 通知"""

    def __init__(self, config: dict):
        self._bot_token = str(config.get("TG_BOT_TOKEN") or config.get("bot_token") or "").strip()
        self._chat_id = str(config.get("TG_USER_ID") or config.get("chat_id") or "").strip()
        self._api_host = str(config.get("TG_API_HOST") or "https://api.telegram.org").strip() or "https://api.telegram.org"
        self._proxy_host = str(config.get("TG_PROXY_HOST") or "").strip()
        self._proxy_port = str(config.get("TG_PROXY_PORT") or "").strip()
        self._proxy_auth = str(config.get("TG_PROXY_AUTH") or "").strip()

    def send(self, title: str, message: str) -> bool:
        """发送 Telegram 消息"""
        if not self._bot_token or not self._chat_id:
            logger.warning("Telegram 渠道未配置")
            return False

        proxy = None
        if self._proxy_host and self._proxy_port:
            host = self._proxy_host
            if self._proxy_auth and "@" not in host:
                host = f"{self._proxy_auth}@{host}"
            proxy = f"http://{host}:{self._proxy_port}"

        url = f"{self._api_host.rstrip('/')}/bot{self._bot_token}/sendMessage"
        text = f"{title}\n\n{message}"

        try:
            with httpx.Client(timeout=15, proxy=proxy) as client:
                resp = client.post(
                    url,
                    data={
                        "chat_id": self._chat_id,
                        "text": text,
                        "disable_web_page_preview": "true",
                    },
                )
                data = resp.json() if resp.content else {}
                if resp.is_success and data.get("ok") is True:
                    logger.info(f"Telegram 通知发送成功，标题：{title}")
                    return True
                logger.error(f"Telegram 通知发送失败，状态码：{resp.status_code}，响应：{resp.text}")
        except Exception as e:
            logger.error(f"Telegram 通知发送异常：{e}")
        return False
