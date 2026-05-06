"""
SMTP 邮件通知渠道
"""
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr

from app.utils.logger import get_logger

logger = get_logger(__name__)


class SmtpChannel:
    """SMTP 邮件通知"""

    def __init__(self, config: dict):
        smtp_server = str(config.get("SMTP_SERVER") or config.get("host") or "").strip()
        host, port = self._parse_server(smtp_server, config.get("port"))

        self._host = host
        self._port = port
        self._ssl = str(config.get("SMTP_SSL") or "false").lower() == "true"
        self._email = str(config.get("SMTP_EMAIL") or config.get("username") or "").strip()
        self._password = str(config.get("SMTP_PASSWORD") or config.get("password") or "").strip()
        self._name = str(config.get("SMTP_NAME") or "PT-Accelerator").strip() or "PT-Accelerator"

    def send(self, title: str, message: str) -> bool:
        """发送邮件"""
        if not self._host or not self._email:
            logger.warning("SMTP 渠道未配置")
            return False

        try:
            msg = MIMEText(message, "plain", "utf-8")
            msg["Subject"] = Header(title, "utf-8")
            msg["From"] = formataddr((Header(self._name, "utf-8").encode(), self._email))
            msg["To"] = formataddr((Header(self._name, "utf-8").encode(), self._email))

            if self._ssl:
                server = smtplib.SMTP_SSL(self._host, self._port, timeout=15)
            else:
                server = smtplib.SMTP(self._host, self._port, timeout=15)
                server.ehlo()
                server.starttls()

            with server:
                server.login(self._email, self._password)
                server.sendmail(self._email, [self._email], msg.as_string())

            logger.info(f"SMTP 通知发送成功，标题：{title}")
            return True
        except Exception as e:
            logger.error(f"SMTP 通知发送异常：{e}")
        return False

    @staticmethod
    def _parse_server(server: str, fallback_port) -> tuple[str, int]:
        if not server:
            return "", int(fallback_port or 465)

        if ":" in server:
            host, port_str = server.rsplit(":", 1)
            try:
                return host.strip(), int(port_str)
            except ValueError:
                return server.strip(), int(fallback_port or 465)

        return server.strip(), int(fallback_port or 465)
