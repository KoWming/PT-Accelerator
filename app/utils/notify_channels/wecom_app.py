"""
企业微信应用通知渠道
"""
import json

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


class WecomAppChannel:
    """企业微信应用通知"""

    def __init__(self, config: dict):
        self._origin = str(config.get("QYWX_ORIGIN") or "https://qyapi.weixin.qq.com").rstrip("/")
        self._qywx_am = str(config.get("QYWX_AM") or "").strip()

    def send(self, title: str, message: str) -> bool:
        if not self._qywx_am:
            logger.warning("企业微信应用渠道未配置")
            return False

        parts = [part.strip() for part in self._qywx_am.split(",") if part.strip()]
        if len(parts) < 4:
            logger.error("企业微信应用渠道配置不完整")
            return False

        corpid, corpsecret, touser, agentid = parts[:4]
        media_id = parts[4] if len(parts) > 4 else ""

        try:
            access_token = self._get_access_token(corpid, corpsecret)
            if not access_token:
                return False

            payload = {
                "touser": touser,
                "agentid": agentid,
            }

            if media_id:
                payload.update({
                    "msgtype": "mpnews",
                    "mpnews": {
                        "articles": [{
                            "title": title,
                            "thumb_media_id": media_id,
                            "author": "PT-Accelerator",
                            "content_source_url": "",
                            "content": message.replace("\n", "<br/>"),
                            "digest": message,
                        }]
                    },
                })
            else:
                payload.update({
                    "msgtype": "text",
                    "text": {"content": f"{title}\n\n{message}"},
                    "safe": "0",
                })

            send_url = f"{self._origin}/cgi-bin/message/send?access_token={access_token}"
            with httpx.Client(timeout=15) as client:
                response = client.post(send_url, content=json.dumps(payload, ensure_ascii=False).encode("utf-8"))
                data = response.json() if response.content else {}
                if response.is_success and data.get("errmsg") == "ok":
                    logger.info(f"企业微信应用通知发送成功，标题：{title}")
                    return True
                logger.error(f"企业微信应用通知发送失败，状态码：{response.status_code}，响应：{response.text}")
        except Exception as e:
            logger.error(f"企业微信应用通知发送异常：{e}")

        return False

    def _get_access_token(self, corpid: str, corpsecret: str) -> str:
        url = f"{self._origin}/cgi-bin/gettoken"
        try:
            with httpx.Client(timeout=15) as client:
                response = client.post(url, params={"corpid": corpid, "corpsecret": corpsecret})
                data = response.json() if response.content else {}
                token = str(data.get("access_token") or "")
                if response.is_success and token:
                    return token
                logger.error(f"企业微信应用获取 access_token 失败，状态码：{response.status_code}，响应：{response.text}")
        except Exception as e:
            logger.error(f"企业微信应用获取 access_token 异常：{e}")
        return ""
