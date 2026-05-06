"""
小米路由器 Hosts 同步服务

基于 gorouter.info 云端 API，将 CFST 优选结果同步到小米路由器的 hosts 文件。
API 参考：MIHosts MoviePilot 插件（gorouter.info）

功能：
  - 测试连接（验证 token 有效性）
  - 获取远程 hosts 列表
  - 同步 CFST 优选结果到远程 hosts
"""
import re
from urllib.parse import urlparse

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)

# gorouter.info API 地址
GOROUTER_API_BASE = "https://www.gorouter.info/api-third-party/service/internal"


class MiHostsService:
    """小米路由器 Hosts 同步服务"""

    def __init__(
        self,
        app_id: str = "",
        device_id: str = "",
        client_id: str = "",
        scope: str = "",
        token: str = "",
        ignore: str = "",
    ):
        self._app_id = app_id
        self._device_id = device_id
        self._client_id = client_id
        self._scope = scope
        self._token = token
        self._ignore = ignore

    def init_config(
        self,
        app_id: str,
        device_id: str,
        client_id: str,
        scope: str,
        token: str,
        ignore: str,
    ) -> None:
        """从配置初始化"""
        self._app_id = app_id
        self._device_id = device_id
        self._client_id = client_id
        self._scope = scope
        self._token = token
        self._ignore = ignore

    @property
    def is_enabled(self) -> bool:
        """是否已配置有效凭据"""
        return bool(self._token)

    def _get_headers(self) -> dict:
        """构建请求头"""
        return {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

    def _make_request(
        self, method: str, endpoint: str, params: dict | None = None, json_data: dict | None = None
    ) -> dict | None:
        """
        发送请求到 gorouter.info API

        Args:
            method: HTTP 方法
            endpoint: API 端点路径
            params: URL 查询参数
            json_data: JSON 请求体

        Returns:
            dict | None: 响应 JSON，失败返回 None
        """
        if not self._token:
            logger.error("小米路由器 token 未配置，无法发起请求")
            return None

        url = f"{GOROUTER_API_BASE}/{endpoint.lstrip('/')}"

        # 公共查询参数
        common_params = {
            "app_id": self._app_id,
            "device_id": self._device_id,
            "client_id": self._client_id,
            "scope": self._scope,
            "token": self._token,
        }
        if params:
            common_params.update(params)

        try:
            with httpx.Client(timeout=15, follow_redirects=True) as client:
                logger.info(f"正在请求小米路由器 API：{method} {url}")

                if method.upper() == "GET":
                    resp = client.get(url, headers=self._get_headers(), params=common_params)
                elif method.upper() == "POST":
                    resp = client.post(url, headers=self._get_headers(), params=common_params, json=json_data)
                else:
                    logger.error(f"不支持的 HTTP 方法：{method}")
                    return None

                resp.raise_for_status()
                result = resp.json()
                logger.info(f"小米路由器 API 响应：{result}")
                return result

        except httpx.TimeoutException:
            logger.error("小米路由器 API 请求超时，请检查网络连接")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"小米路由器 API HTTP 错误：{e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"小米路由器 API 请求异常：{type(e).__name__}: {e}")
            return None

    def test_connection(self) -> tuple[bool, str]:
        """
        测试连接，验证 token 是否有效

        Returns:
            (success: bool, message: str)
        """
        if not self._token:
            return False, "未配置小米路由器 Token"

        result = self._make_request("GET", "/custom_host_get")
        if result is None:
            return False, "请求失败，请检查 Token 和网络连接"

        # 常见错误码判断
        if result.get("code") == 401 or result.get("error"):
            return False, "Token 无效或已过期，请重新获取"

        return True, "连接成功"

    def get_remote_hosts(self) -> tuple[list[dict], str]:
        """
        获取小米路由器当前的 hosts 内容

        Returns:
            (hosts: list[dict], raw_text: str)
            - hosts: 解析后的 hosts 列表 [{"domain": "xxx", "ip": "xxx"}, ...]
            - raw_text: 原始 hosts 文本内容
        """
        result = self._make_request("GET", "/custom_host_get")
        if result is None:
            return [], ""

        # 响应格式：{"code": 0, "data": {"hosts": "1.2.3.4 domain.com\n..."}}
        data = result.get("data", {})
        raw_text = data.get("hosts", "") or ""

        hosts: list[dict] = []
        for line in raw_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # 格式：IP 域名 [备注...]
            # 例如：104.21.0.1 tracker.example.com CF
            parts = line.split()
            if len(parts) >= 2:
                ip = parts[0]
                domain = parts[1]
                # 简单 IP 格式校验
                if self._is_valid_ip(ip):
                    hosts.append({"domain": domain, "ip": ip, "raw": line})

        logger.info(f"获取到小米路由器远程 hosts {len(hosts)} 条")
        return hosts, raw_text

    def sync_hosts(self, cf_hosts: list[dict]) -> tuple[bool, str]:
        """
        将 CFST 优选结果同步到小米路由器 hosts

        合并策略：
          1. 获取远程 hosts 列表
          2. 按域名匹配，用 CFST 结果覆盖目标域名的 IP
          3. 若 tracker 域名在远程 hosts 中存在但 CFST 结果中无，则保留原有记录
          4. 将合并结果写回远程

        Args:
            cf_hosts: CFST 优选结果 [{"domain": "xxx", "ip": "xxx"}, ...]

        Returns:
            (success: bool, message: str)
        """
        if not self._token:
            return False, "未配置小米路由器 Token"

        if not cf_hosts:
            return False, "没有需要同步的 CFST 结果"

        # ── 步骤 1：获取远程 hosts ──────────────────────────────────
        logger.info("正在获取小米路由器远程 hosts…")
        remote_hosts, _raw_text = self.get_remote_hosts()
        if remote_hosts is None:
            return False, "无法获取远程 hosts，请检查网络连接"

        # 构建远程域名 → 原始行索引的映射（用于定位和替换）
        remote_domain_map: dict[str, dict] = {}
        for entry in remote_hosts:
            domain = entry.get("domain", "")
            if domain:
                remote_domain_map[domain] = entry

        # ── 步骤 2：构建合并后的 hosts 文本 ──────────────────────────
        # 用 CFST 结果覆盖远程记录
        cf_domain_map = {h.get("domain", ""): h.get("ip", "") for h in cf_hosts if h.get("domain")}

        merged_lines: list[str] = []
        seen_domains: set[str] = set()

        # 先处理 CFST 结果（优先写入）
        for host in cf_hosts:
            domain = host.get("domain", "").strip()
            ip = host.get("ip", "").strip()
            if not domain or not ip:
                continue

            merged_lines.append(f"{ip} {domain}")
            seen_domains.add(domain)
            logger.info(f"CFST 同步：{domain} -> {ip}")

        # 再处理远程 hosts 中不在 CFST 结果里的条目（保留原有自定义记录）
        ignored_domains = set(self._ignore.splitlines()) if self._ignore else set()
        for entry in remote_hosts:
            domain = entry.get("domain", "")
            ip = entry.get("ip", "")
            if not domain or domain in seen_domains:
                continue
            if domain in ignored_domains:
                continue

            merged_lines.append(f"{ip} {domain}")

        merged_text = "\n".join(merged_lines)
        logger.info(f"合并后 hosts 共 {len(merged_lines)} 条，将同步到小米路由器")

        # ── 步骤 3：写入远程 hosts ──────────────────────────────────
        write_result = self._make_request(
            "POST",
            "/custom_host_set",
            json_data={"hosts": merged_text},
        )

        if write_result is None:
            return False, "写入 hosts 失败，请检查网络连接"

        if write_result.get("code") == 0 or write_result.get("success"):
            logger.info("小米路由器 hosts 同步完成")
            return True, f"成功同步 {len(cf_hosts)} 条 CFST 结果到小米路由器（共 {len(merged_lines)} 条 hosts）"
        else:
            error_msg = write_result.get("message") or write_result.get("error") or "未知错误"
            logger.error(f"小米路由器 hosts 写入失败：{error_msg}")
            return False, f"写入失败：{error_msg}"

    # ──────────────────────────── 工具方法 ────────────────────────────────

    @staticmethod
    def _is_valid_ip(ip: str) -> bool:
        """简单校验是否为有效 IPv4"""
        pattern = r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})$"
        return bool(re.match(pattern, ip))
