"""
通知渠道服务

通知渠道配置存储在 config.notify.channels。
支持类型定义来自 frontend/src/shared/notify-meta.json，确保前后端通知元数据保持一致。
"""
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx


from app.utils.logger import get_logger
from app.utils.notify_channels.bark import BarkChannel
from app.utils.notify_channels.chat import ChatChannel
from app.utils.notify_channels.dingtalk import DingTalkChannel
from app.utils.notify_channels.feishu import FeishuChannel
from app.utils.notify_channels.igot import IgotChannel
from app.utils.notify_channels.mediasaber import MediaSaberChannel
from app.utils.notify_channels.serverj import ServerJChannel
from app.utils.notify_channels.slack import SlackChannel
from app.utils.notify_channels.smtp import SmtpChannel
from app.utils.notify_channels.telegram import TelegramChannel
from app.utils.notify_channels.wecom import WecomChannel
from app.utils.notify_channels.wecom_app import WecomAppChannel
from app.utils.notify_channels.webhook import WebhookChannel

logger = get_logger(__name__)

NOTIFY_META_PATH = Path(__file__).resolve().parents[2] / "frontend" / "src" / "utils" / "notify-meta.json"
with NOTIFY_META_PATH.open("r", encoding="utf-8") as f:
    NOTIFY_META = json.load(f)

TYPE_ALIASES = NOTIFY_META.get("aliases", {})
COMMON_CONFIG_FIELDS = NOTIFY_META.get("commonFields", [])
TYPE_META_MAP = {item["type"]: item for item in NOTIFY_META.get("types", [])}
TYPE_FIELD_MAP = {item["type"]: item.get("fields", []) for item in NOTIFY_META.get("types", [])}

# 支持的通知渠道类型
SUPPORTED_TYPES = [item["type"] for item in NOTIFY_META.get("types", [])]



def _canonicalize_type(channel_type: str) -> str:
    """将兼容别名收口到标准类型。"""
    normalized = (channel_type or "").strip()
    return TYPE_ALIASES.get(normalized, normalized)


def _validate_type(channel_type: str) -> bool:
    """验证渠道类型"""
    return _canonicalize_type(channel_type) in SUPPORTED_TYPES


def _should_keep_config_value(value) -> bool:
    """过滤空配置值，避免写入大量无意义字段。"""
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    return True


def _sanitize_config(channel_type: str, config: dict) -> dict:
    """仅保留当前渠道真正需要的配置项。"""
    canonical_type = _canonicalize_type(channel_type)
    allowed_fields = [*COMMON_CONFIG_FIELDS, *(TYPE_FIELD_MAP.get(canonical_type, []))]
    raw_config = config or {}
    sanitized: dict = {}

    for key in allowed_fields:
        value = raw_config.get(key)
        if _should_keep_config_value(value):
            sanitized[key] = value

    return sanitized


def _gen_id(channel_type: str, name: str) -> str:
    """根据 type+name 生成渠道ID"""
    canonical_type = _canonicalize_type(channel_type)
    key = f"{canonical_type}:{name.strip().lower()}"
    return hashlib.md5(key.encode()).hexdigest()[:8]


NOTIFY_SEPARATOR = "──────────"
HITOKOTO_API_URLS = [
    "https://v1.hitokoto.cn/?encode=json",
    "https://yyapi.xpdbk.com/api/ian",
    "https://api.nxvav.cn/api/yiyan/",
]
HITOKOTO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7",
}
DEFAULT_HITOKOTO_TEXT = "妹妹说紫色很有韵味！"


def _fetch_hitokoto_text(timeout_seconds: float = 3.0) -> str:
    """获取一言随机句子，失败时尝试多个接口，全部失败再返回默认文案。"""
    for url in HITOKOTO_API_URLS:
        try:
            response = httpx.get(url, headers=HITOKOTO_HEADERS, timeout=timeout_seconds)
            response.raise_for_status()

            content = ""
            source = ""

            try:
                data = response.json()
                if isinstance(data, dict):
                    content = str(
                        data.get("hitokoto")
                        or data.get("yiyan")
                        or data.get("text")
                        or data.get("content")
                        or ""
                    ).strip()
                    source = str(
                        data.get("from")
                        or data.get("source")
                        or data.get("nick")
                        or ""
                    ).strip()
            except Exception:
                content = response.text.strip()

            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1].strip()

            if content:
                return f"{content} —— {source}" if source else content

        except Exception as e:
            logger.debug(f"获取一言失败，接口：{url}，错误：{e}")

    logger.debug("所有一言接口均不可用，使用默认尾文")
    return DEFAULT_HITOKOTO_TEXT


def _stringify_notify_value(value) -> str:
    if value is None:
        return "未知"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def build_structured_notification(
    *,
    header: str,
    task_type: str,
    success: bool,
    detail_title: str | None = None,
    detail_items: list[tuple[str, object]] | None = None,
    result_text: str | None = None,
    push_time: datetime | None = None,
    footer: str = "",
) -> tuple[str, str]:
    """构建统一样式的结构化通知文本。"""
    push_time = push_time or datetime.now()
    detail_items = detail_items or []
    lines = [
        NOTIFY_SEPARATOR,
        f"📌 任务类型：{task_type}",
        f"{'✅' if success else '❌'} 执行结果：{result_text or ('任务完成' if success else '任务失败')}",
    ]

    if detail_title and detail_items:
        lines.extend([
            NOTIFY_SEPARATOR,
            f"📊 {detail_title}：",
        ])
        for label, value in detail_items:
            lines.append(f"• {label}：{_stringify_notify_value(value)}")

    lines.extend([
        NOTIFY_SEPARATOR,
        f"⏰ 推送时间：{push_time.strftime('%Y-%m-%d %H:%M:%S')}",
    ])

    if footer:
        lines.extend(["", footer])

    return f"【🚀 {header}】", "\n".join(lines)


class NotifyService:
    """通知渠道管理服务"""

    CHANNEL_CLASS_MAP = {
        "wecom_bot": WecomChannel,
        "wecom_app": WecomAppChannel,
        "telegram": TelegramChannel,
        "igot": IgotChannel,
        "dingding": DingTalkChannel,
        "feishu": FeishuChannel,
        "smtp": SmtpChannel,
        "bark": BarkChannel,
        "serverj": ServerJChannel,
        "chat": ChatChannel,
        "mediasaber": MediaSaberChannel,
        "slack": SlackChannel,
        "webhook": WebhookChannel,
    }

    def __init__(self):
        pass

    def _get_channels(self) -> list[dict]:
        """获取 notify.channels 列表"""
        from app.config import config
        return config.get("notify.channels", default=[])

    def _save_channels(self, channels: list[dict]):
        """保存 notify.channels 列表"""
        from app.config import config
        config.set("notify.channels", channels)
        config.save()

    def _find_by_id(self, channel_id: str) -> Optional[tuple[int, dict]]:
        """根据ID查找渠道，返回 (index, item) 或 None"""
        channels = self._get_channels()
        for i, ch in enumerate(channels):
            if ch.get("id") == channel_id:
                return i, ch
        return None

    def _find_by_name(self, name: str) -> Optional[tuple[int, dict]]:
        """根据名称查找渠道"""
        channels = self._get_channels()
        name_lower = name.strip().lower()
        for i, ch in enumerate(channels):
            if ch.get("name", "").strip().lower() == name_lower:
                return i, ch
        return None

    def list_channels(self) -> list[dict]:
        """列出所有通知渠道"""
        return self._get_channels().copy()

    def get_channel(self, channel_id: str) -> Optional[dict]:
        """根据ID获取单个渠道"""
        result = self._find_by_id(channel_id)
        return result[1].copy() if result else None

    def add_channel(
        self,
        name: str,
        channel_type: str,
        config: dict,
        enabled: bool = True,
    ) -> dict:
        """
        添加新的通知渠道。

        Returns:
            新渠道字典（包含id）

        Raises:
            ValueError: 无效的类型或名称重复
        """
        canonical_type = _canonicalize_type(channel_type)
        if not _validate_type(canonical_type):
            raise ValueError(f"不支持的通知渠道类型: {channel_type}，支持的类型: {', '.join(SUPPORTED_TYPES)}")

        name = name.strip()
        if not name:
            raise ValueError("渠道名称不能为空")

        existing = self._find_by_name(name)
        if existing:
            raise ValueError(f"通知渠道名称已存在: {name}")

        channel_id = _gen_id(canonical_type, name)

        item = {
            "id": channel_id,
            "name": name,
            "type": canonical_type,
            "enabled": enabled,
            "config": _sanitize_config(canonical_type, config),
        }

        channels = self._get_channels()
        channels.append(item)
        self._save_channels(channels)

        logger.info(f"通知渠道已添加：{name}（{canonical_type}），ID={channel_id}")
        return item.copy()

    def update_channel(
        self,
        channel_id: str,
        name: Optional[str] = None,
        channel_type: Optional[str] = None,
        config: Optional[dict] = None,
        enabled: Optional[bool] = None,
    ) -> Optional[dict]:
        """
        更新渠道（部分更新）。

        Returns:
            更新后的渠道字典，未找到返回 None

        Raises:
            ValueError: 无效的类型或名称重复
        """
        result = self._find_by_id(channel_id)
        if not result:
            return None

        idx, item = result
        channels = self._get_channels()

        if name is not None:
            name = name.strip()
            if not name:
                raise ValueError("渠道名称不能为空")
            existing = self._find_by_name(name)
            if existing and existing[0] != idx:
                raise ValueError(f"通知渠道名称已存在: {name}")
            item["name"] = name

        if channel_type is not None:
            canonical_type = _canonicalize_type(channel_type)
            if not _validate_type(canonical_type):
                raise ValueError(f"不支持的通知渠道类型: {channel_type}，支持的类型: {', '.join(SUPPORTED_TYPES)}")
            item["type"] = canonical_type

        if config is not None:
            item["config"] = _sanitize_config(item.get("type", ""), config)

        if enabled is not None:
            item["enabled"] = enabled

        item.pop("created_at", None)
        item.pop("updated_at", None)
        channels[idx] = item
        self._save_channels(channels)

        logger.info(f"通知渠道已更新：ID={channel_id}，名称={item['name']}")
        return item.copy()

    def delete_channel(self, channel_id: str) -> bool:
        """
        根据ID删除渠道。

        Returns:
            True 已删除，False 未找到
        """
        result = self._find_by_id(channel_id)
        if not result:
            return False

        idx, item = result
        channels = self._get_channels()
        channels.pop(idx)
        self._save_channels(channels)

        logger.info(f"通知渠道已删除：ID={channel_id}，名称={item['name']}")
        return True

    def send(self, channel_id: str, title: str, message: str) -> bool:
        """
        向指定渠道发送通知。

        Args:
            channel_id: 渠道ID（支持 "default" 或具体ID）
            title: 通知标题
            message: 通知内容

        Returns:
            是否发送成功
        """
        if channel_id == "default":
            channels = self._get_channels()
            success = True
            for ch in channels:
                if ch.get("enabled", False):
                    if not self._send_to_channel(ch, title, message):
                        success = False
            return success

        result = self._find_by_id(channel_id)
        if not result:
            logger.warning(f"通知渠道不存在: {channel_id}")
            return False

        _, item = result
        return self._send_to_channel(item, title, message)

    def _build_channel_instance(self, channel_type: str, config: dict):
        canonical_type = _canonicalize_type(channel_type)
        channel_cls = self.CHANNEL_CLASS_MAP.get(canonical_type)
        if not channel_cls:
            return None
        return channel_cls(config)

    def _build_message(self, channel: dict, title: str, message: str) -> str:
        """按渠道配置组装最终通知内容。"""
        config = channel.get("config", {}) or {}
        if config.get("HITOKOTO"):
            return f"{message}\n{_fetch_hitokoto_text()}"
        return message

    def _send_to_channel(self, channel: dict, title: str, message: str) -> bool:
        """向单个渠道发送消息"""
        channel_type = channel.get("type", "")
        config = channel.get("config", {})
        channel_name = channel.get("name", channel_type)

        try:
            handler = self._build_channel_instance(channel_type, config)
            if not handler:
                logger.warning(f"暂不支持的通知类型: {channel_type}")
                return False

            final_message = self._build_message(channel, title, message)
            success = handler.send(title, final_message)
            if success:
                logger.info(f"通知已发送到 {channel_name}")
            else:
                logger.warning(f"通知发送到 {channel_name} 失败")
            return success

        except Exception as e:
            logger.error(f"发送通知到 {channel_name} 失败: {e}")
            return False

    def test_channel(self, channel_id: str) -> dict:
        """
        测试渠道连接/发送。

        Returns:
            {"success": bool, "message": str}
        """
        result = self._find_by_id(channel_id)
        if not result:
            return {"success": False, "message": f"渠道不存在: {channel_id}"}

        _, item = result
        channel_type = item["type"]
        config = item.get("config", {})

        try:
            handler = self._build_channel_instance(channel_type, config)
            if not handler:
                return {"success": False, "message": f"暂不支持测试类型: {channel_type}"}

            success = handler.send(
                "测试通知",
                self._build_message(item, "测试通知", "这是一条来自 PT-Accelerator 的测试消息")
            )
            if success:
                return {"success": True, "message": "测试消息发送成功"}
            return {"success": False, "message": "测试消息发送失败"}
        except Exception as e:
            logger.error(f"通知渠道测试失败: {channel_id} - {e}")
            return {"success": False, "message": f"测试失败: {str(e)}"}

    @staticmethod
    def get_supported_types() -> list[dict]:
        """获取支持的渠道类型列表"""
        return [
            {
                "type": channel_type,
                "name": meta.get("label", channel_type),
                "fields": [*COMMON_CONFIG_FIELDS, *(meta.get("fields", []))],
            }
            for channel_type, meta in TYPE_META_MAP.items()
        ]



# 全局单例
notify_service = NotifyService()
