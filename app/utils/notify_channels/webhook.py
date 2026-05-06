"""
Webhook 通知渠道
"""
import json

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


class WebhookChannel:
    """自定义 Webhook 通知"""

    def __init__(self, config: dict):
        self._url = str(config.get("WEBHOOK_URL") or config.get("url") or "").strip()
        self._method = str(config.get("WEBHOOK_METHOD") or config.get("method") or "POST").upper()
        self._content_type = str(config.get("WEBHOOK_CONTENT_TYPE") or "application/json").strip() or "application/json"
        self._headers = str(config.get("WEBHOOK_HEADERS") or config.get("headers") or "")
        self._body = str(config.get("WEBHOOK_BODY") or "").strip()

    def send(self, title: str, message: str) -> bool:
        if not self._url:
            logger.warning("Webhook 渠道未配置")
            return False

        headers = self._parse_headers()
        headers.setdefault("Content-Type", self._content_type)
        body_template = self._body or '{"title": "$title", "text": "$content"}'
        rendered_body = (
            self._render_json_template(body_template, title, message)
            if self._method != "GET" and self._content_type == "application/json"
            else self._render_value(body_template, title, message)
        )

        request_kwargs: dict = {"headers": headers}
        if self._method == "GET":
            request_kwargs["params"] = self._parse_query_params(rendered_body)
        else:
            if self._content_type == "application/json":
                try:
                    request_kwargs["json"] = json.loads(rendered_body)
                except json.JSONDecodeError:
                    request_kwargs["content"] = rendered_body.encode("utf-8")
            elif self._content_type == "application/x-www-form-urlencoded":
                request_kwargs["data"] = self._parse_query_params(rendered_body)
            else:
                request_kwargs["content"] = rendered_body.encode("utf-8")

        try:
            with httpx.Client(timeout=15) as client:
                response = client.request(self._method, self._url, **request_kwargs)
                if response.is_success:
                    logger.info(f"Webhook 通知发送成功，标题：{title}")
                    return True
                logger.error(f"Webhook 通知发送失败，状态码：{response.status_code}，响应：{response.text}")
        except Exception as e:
            logger.error(f"Webhook 通知发送异常：{e}")
        return False

    def _parse_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        for line in self._headers.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key:
                headers[key] = value
        return headers

    @staticmethod
    def _render_value(value: str, title: str, message: str) -> str:
        return value.replace("$title", title).replace("$content", message)

    @staticmethod
    def _render_json_template(value: str, title: str, message: str) -> str:
        return value.replace("$title", json.dumps(title, ensure_ascii=False)[1:-1]).replace(
            "$content",
            json.dumps(message, ensure_ascii=False)[1:-1],
        )

    @staticmethod
    def _parse_query_params(value: str) -> dict[str, str]:
        pairs: dict[str, str] = {}
        for item in value.split("&"):
            if not item:
                continue
            if "=" in item:
                key, val = item.split("=", 1)
            else:
                key, val = item, ""
            key = key.strip()
            if key:
                pairs[key] = val
        return pairs
