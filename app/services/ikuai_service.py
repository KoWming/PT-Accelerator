"""
爱快 DNS 同步服务

支持：
  - 登录认证（MD5 密码）
  - DNS 记录查询
  - DNS 记录添加/删除
  - 通配符域名支持
"""
import hashlib
import json
from urllib.parse import urlparse

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)

# 爱快 API 返回码（旧固件格式）
IKUAI_LOGIN_SUCCESS = 10000
IKUAI_DNS_SUCCESS = 30000


def _is_ikuai_success(result: dict) -> bool:
    """
    兼容爱快两种固件响应格式：
      - 旧格式：{"Result": 30000, "Data": {...}}
      - 新格式：{"code": 0, "message": "Success", ...}
    """
    # 旧格式
    if "Result" in result:
        return result["Result"] == IKUAI_DNS_SUCCESS
    # 新格式
    if "code" in result:
        return result["code"] == 0
    return False


def _ikuai_get_dns_records(result: dict) -> list:
    """
    从查询响应中取出 DNS 记录列表，兼容两种格式：
      - 旧格式：result["Data"]["data"]
      - 新格式：result["results"]["data"]
    """
    if "Data" in result:
        return result.get("Data", {}).get("data", [])
    if "results" in result:
        return result.get("results", {}).get("data", [])
    return []


class IkuaiService:
    """爱快路由 DNS 同步服务"""

    @staticmethod
    def _normalize_endpoint(host: str, port: int | None = None) -> tuple[str, int, bool, str]:
        """规范化爱快地址，协议直接由 host 字段中的 URL 前缀决定。"""
        raw_host = str(host or "").strip().rstrip("/")
        if not raw_host:
            normalized_port = port or 80
            return "", normalized_port, False, ""

        parsed = urlparse(raw_host if "://" in raw_host else f"http://{raw_host}")
        use_https = parsed.scheme.lower() == "https"
        hostname = parsed.hostname or raw_host
        normalized_port = port or parsed.port or (443 if use_https else 80)
        scheme = "https" if use_https else "http"
        base_url = f"{scheme}://{hostname}:{normalized_port}"
        return hostname, normalized_port, use_https, base_url

    def __init__(self, host: str = "", port: int | None = None, username: str = "admin", password: str = ""):
        normalized_host, normalized_port, normalized_use_https, base_url = self._normalize_endpoint(host, port)
        self._host = normalized_host
        self._port = normalized_port
        self._username = username
        self._password = password
        self._use_https = normalized_use_https
        self._base_url = base_url
        self._session: httpx.Client | None = None
        self._logged_in = False
        self._last_sync_success = False

    def init_config(self, host: str, port: int | None, username: str, password: str):
        """初始化配置"""
        normalized_host, normalized_port, normalized_use_https, base_url = self._normalize_endpoint(host, port)
        self._host = normalized_host
        self._port = normalized_port
        self._use_https = normalized_use_https
        self._base_url = base_url
        self._username = username
        self._password = password
        self._session = httpx.Client(timeout=10, verify=normalized_use_https)
        self._logged_in = False

    @property
    def is_enabled(self) -> bool:
        """是否已配置"""
        return bool(self._host and self._password)

    def _get_headers(self) -> dict:
        """获取请求头"""
        return {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Origin": self._base_url,
            "Referer": f"{self._base_url}/",
        }

    def _get_login_params(self) -> dict:
        """生成登录参数（MD5 密码）"""
        password_md5 = hashlib.md5(self._password.encode("utf-8")).hexdigest()
        return {
            "username": self._username,
            "passwd": password_md5,
        }

    def login(self) -> bool:
        """登录爱快路由器"""
        if self._logged_in:
            return True

        if not self._session:
            self._session = httpx.Client(timeout=10)

        # 类型断言：确保 session 不为 None
        session = self._session

        try:
            url = f"{self._base_url}/Action/login"
            params = self._get_login_params()
            logger.info(f"正在登录爱快路由器：{url}")

            resp = session.post(url, json=params, headers=self._get_headers())
            resp.raise_for_status()

            data = resp.json()
            if data.get("Result") == IKUAI_LOGIN_SUCCESS:
                self._logged_in = True
                # 保存登录 cookies
                session.cookies.update(resp.cookies)
                logger.info("爱快路由器登录成功")
                return True
            else:
                logger.error(f"爱快路由器登录失败：{data}")
                return False

        except httpx.ConnectError:
            logger.error("爱快路由器登录异常：无法连接到服务器，请检查地址、端口或网络")
            return False
        except httpx.RemoteProtocolError:
            logger.error("爱快路由器登录异常：服务器断开连接，请确认爱快 Web 管理功能已启用")
            return False
        except Exception:
            logger.error("爱快路由器登录异常：请求失败")
            return False

    def test_connection(self) -> tuple[bool, str]:
        """
        测试连接

        Returns:
            (success: bool, message: str)
        """
        if not self._host:
            return False, "未配置爱快路由器地址"

        if not self._password:
            return False, "未配置爱快路由器密码"

        if self.login():
            return True, "连接成功"
        else:
            return False, "登录失败，请检查地址、用户名、密码"

    def get_dns_records(self) -> list:
        """获取现有的 DNS 记录"""
        if not self.login():
            return []

        if not self._session:
            return []

        try:
            url = f"{self._base_url}/Action/call"
            payload = {
                "func_name": "dns",
                "action": "show",
                "param": {
                    "TYPE": "dns_proxy_total,dns_proxy",
                    "FINDS": "domain,dns_addr,src_addr,comment",
                    "KEYWORDS": "",
                    "limit": "0,200",
                    "ORDER_BY": "",
                    "ORDER": "",
                },
            }

            resp = self._session.post(url, json=payload, headers=self._get_headers())

            if resp.status_code == 200:
                result = resp.json()
                if _is_ikuai_success(result):
                    records = _ikuai_get_dns_records(result)
                    logger.info(f"获取到 {len(records)} 条 DNS 记录")
                    return records
                else:
                    logger.error(f"获取 DNS 记录失败：{result}")
                    return []
            else:
                logger.error(f"获取 DNS 记录请求失败，状态码：{resp.status_code}")
                return []

        except httpx.ConnectError:
            logger.error("获取 DNS 记录异常：无法连接到爱快路由器")
            return []
        except httpx.RemoteProtocolError:
            logger.error("获取 DNS 记录异常：服务器断开连接")
            return []
        except Exception:
            logger.error("获取 DNS 记录异常：请求失败")
            return []

    def _delete_dns_record(self, record_id: str) -> bool:
        """删除单条 DNS 记录"""
        if not self.login():
            return False

        if not self._session:
            return False

        try:
            url = f"{self._base_url}/Action/call"
            delete_data = {
                "func_name": "dns",
                "action": "del",
                "param": {
                    "id": record_id,
                },
            }

            resp = self._session.post(url, json=delete_data, headers=self._get_headers())
            if resp.status_code == 200:
                result = resp.json()
                if _is_ikuai_success(result):
                    logger.info(f"成功删除 DNS 记录：ID={record_id}")
                    return True
                else:
                    logger.error(f"删除 DNS 记录失败：{result}")
                    return False
            return False

        except httpx.ConnectError:
            logger.error("删除 DNS 记录异常：无法连接到爱快路由器")
            return False
        except Exception:
            logger.error("删除 DNS 记录异常：请求失败")
            return False

    def _delete_dns_records_batch(self, record_ids: list[str]) -> bool:
        """
        批量删除 DNS 记录（一次请求删除多条）。

        使用逗号拼接 ID，如 {"id": "1,2,3"}。
        部分固件不支持此格式，失败时由调用方降级为逐条删除。

        Args:
            record_ids: 要删除的记录 ID 列表

        Returns:
            bool: 批量删除是否成功
        """
        if not self.login():
            return False

        if not record_ids or not self._session:
            return False

        ids_str = ",".join(record_ids)
        try:
            url = f"{self._base_url}/Action/call"
            delete_data = {
                "func_name": "dns",
                "action": "del",
                "param": {
                    "id": ids_str,
                },
            }

            resp = self._session.post(url, json=delete_data, headers=self._get_headers())
            if resp.status_code == 200:
                result = resp.json()
                if _is_ikuai_success(result):
                    logger.info(f"批量删除 DNS 记录成功：共 {len(record_ids)} 条（ID: {ids_str}）")
                    return True
                else:
                    logger.warning(f"批量删除 DNS 记录失败，将降级为逐条删除：{result}")
                    return False
            logger.warning(f"批量删除 DNS 记录请求失败（状态码 {resp.status_code}），将降级为逐条删除")
            return False

        except httpx.ConnectError:
            logger.error("批量删除 DNS 记录异常：无法连接到爱快路由器")
            return False
        except Exception:
            logger.warning("批量删除 DNS 记录异常，将降级为逐条删除")
            return False

    def _delete_existing_dns_record_by_domain(self, domain: str) -> None:
        """删除指定域名的已存在 DNS 记录（支持通配符匹配）"""
        try:
            logger.info(f"正在检查并删除已存在的 DNS 记录：{domain}")
            records = self.get_dns_records()

            if not records:
                logger.info("未获取到任何 DNS 记录")
                return

            for record in records:
                record_domain = record.get("domain", "")
                # 检查精确匹配或通配符匹配
                if record_domain == domain or (
                    record_domain.startswith("*.")
                    and domain.endswith(record_domain[2:])
                ):
                    record_id = record.get("id")
                    if not record_id:
                        continue

                    logger.info(
                        f"找到匹配的记录：ID={record_id}, Domain={record_domain}, "
                        f"IP={record.get('dns_addr')}, Comment={record.get('comment')}"
                    )
                    self._delete_dns_record(str(record_id))

        except Exception:
            logger.error("删除 DNS 记录时发生错误")

    def _convert_to_wildcard(self, domain: str) -> str:
        """
        将域名转换为通配符格式

        例如：
          - kp.m-team.cc -> *.m-team.cc
          - www.example.com -> *.example.com
        """
        if "." in domain:
            # 获取顶级域名部分
            main_domain = ".".join(domain.split(".")[-2:])
            return f"*.{main_domain}"
        return domain

    def add_dns_record(self, domain: str, ip: str, comment: str = "PT优选IP") -> bool:
        """
        添加单条 DNS 记录

        Args:
            domain: 域名
            ip: IP 地址
            comment: 备注

        Returns:
            bool: 是否成功
        """
        if not self.login():
            return False

        if not self._session:
            return False

        try:
            # 先删除已存在的相同域名记录
            self._delete_existing_dns_record_by_domain(domain)

            # 转换为通配符域名
            wildcard_domain = self._convert_to_wildcard(domain)

            data = {
                "func_name": "dns",
                "action": "add",
                "param": {
                    "comment": comment,
                    "dns_addr": ip,
                    "domain": wildcard_domain,
                    "enabled": "yes",
                    "parse_type": "ipv4",
                    "dns_addr_ipv4": ip,
                    "dns_addr_ipv6": "",
                    "dns_addr_proxy": "",
                    "src_addr": "",
                },
            }

            url = f"{self._base_url}/Action/call"
            resp = self._session.post(url, json=data, headers=self._get_headers())

            if resp.status_code == 200:
                # 清理响应文本，只保留 JSON 部分
                json_text = resp.text.split("\n")[0].strip()
                try:
                    result = json.loads(json_text)
                    if _is_ikuai_success(result):
                        logger.info(f"成功添加 DNS 记录：{domain} -> {ip}")
                        return True
                    else:
                        logger.error(f"添加 DNS 记录失败：{domain} -> {ip}, 错误：{result}")
                        return False
                except json.JSONDecodeError:
                    # 如果响应文本包含成功信息，也认为是成功的
                    if "Success" in resp.text and ("Result\":30000" in resp.text or "\"code\":0" in resp.text or "\"code\": 0" in resp.text):
                        logger.info(f"成功添加 DNS 记录：{domain} -> {ip}")
                        return True
                    else:
                        logger.error(f"解析 DNS 记录响应失败：{resp.text}")
                        return False
            return False

        except httpx.ConnectError:
            logger.error("添加 DNS 记录异常：无法连接到爱快路由器")
            return False
        except httpx.RemoteProtocolError:
            logger.error("添加 DNS 记录异常：服务器断开连接")
            return False
        except Exception:
            logger.error("添加 DNS 记录异常：请求失败")
            return False

    def _batch_cleanup_domains(self, domains: set[str], all_records: list[dict]) -> None:
        """
        在已缓存的全量 DNS 记录中，批量删除与目标域名匹配的旧记录。

        策略：优先发一次批量删除请求（{"id": "1,2,3,..."}）；
        若固件不支持批量格式，则降级为逐条删除。

        Args:
            domains: 要清理的域名集合（原始域名，非通配符）
            all_records: 提前查好的全量 DNS 记录列表
        """
        # 收集所有匹配的记录 ID
        matched_ids: list[str] = []
        for record in all_records:
            record_domain = record.get("domain", "")
            for domain in domains:
                if record_domain == domain or (
                    record_domain.startswith("*.") and domain.endswith(record_domain[2:])
                ):
                    record_id = record.get("id")
                    if record_id:
                        matched_ids.append(str(record_id))
                    break  # 每条记录只匹配一次

        if not matched_ids:
            return

        logger.info(f"找到 {len(matched_ids)} 条旧记录需要删除（ID: {','.join(matched_ids)}）")

        # 优先批量删除
        if len(matched_ids) > 1:
            if self._delete_dns_records_batch(matched_ids):
                return
            # 批量失败 → 降级逐条
            logger.info("降级为逐条删除…")

        for record_id in matched_ids:
            self._delete_dns_record(record_id)

    def _add_dns_record_direct(self, domain: str, ip: str, comment: str = "PT优选IP") -> bool:
        """
        直接添加 DNS 记录（不含前置删除逻辑，供批量同步内部使用）。
        调用方应自行保证旧记录已清理。
        """
        if not self._session:
            return False

        try:
            wildcard_domain = self._convert_to_wildcard(domain)
            data = {
                "func_name": "dns",
                "action": "add",
                "param": {
                    "comment": comment,
                    "dns_addr": ip,
                    "domain": wildcard_domain,
                    "enabled": "yes",
                    "parse_type": "ipv4",
                    "dns_addr_ipv4": ip,
                    "dns_addr_ipv6": "",
                    "dns_addr_proxy": "",
                    "src_addr": "",
                },
            }

            url = f"{self._base_url}/Action/call"
            resp = self._session.post(url, json=data, headers=self._get_headers())

            if resp.status_code == 200:
                json_text = resp.text.split("\n")[0].strip()
                try:
                    result = json.loads(json_text)
                    if _is_ikuai_success(result):
                        logger.info(f"成功添加 DNS 记录：{domain} -> {ip}")
                        return True
                    else:
                        logger.error(f"添加 DNS 记录失败：{domain} -> {ip}, 错误：{result}")
                        return False
                except json.JSONDecodeError:
                    if "Success" in resp.text and (
                        "Result\":30000" in resp.text
                        or "\"code\":0" in resp.text
                        or "\"code\": 0" in resp.text
                    ):
                        logger.info(f"成功添加 DNS 记录：{domain} -> {ip}")
                        return True
                    else:
                        logger.error(f"解析 DNS 记录响应失败：{resp.text}")
                        return False
            return False

        except httpx.ConnectError:
            logger.error("添加 DNS 记录异常：无法连接到爱快路由器")
            return False
        except httpx.RemoteProtocolError:
            logger.error("添加 DNS 记录异常：服务器断开连接")
            return False
        except Exception:
            logger.error("添加 DNS 记录异常：请求失败")
            return False

    def sync_hosts_to_dns(self, hosts: list[dict]) -> bool:
        """
        将 hosts 列表同步到爱快 DNS。

        优化策略：
          1. 只在同步开始时查询一次全量 DNS 记录（减少重复请求）
          2. 批量对比并删除所有目标域名的旧记录
          3. 顺序添加全部新记录

        Args:
            hosts: 列表，每个元素为 {"domain": xxx, "ip": xxx}

        Returns:
            bool: 是否同步成功
        """
        self._last_sync_success = False

        if not hosts:
            logger.warning("没有需要同步的 hosts 记录")
            return False

        if not self.login():
            return False

        try:
            valid_hosts = [h for h in hosts if h.get("domain") and h.get("ip")]
            if not valid_hosts:
                logger.warning("过滤后没有有效的 hosts 记录")
                return False

            # ── 步骤 1：一次性获取全量 DNS 记录 ──────────────────────────
            logger.info("正在获取现有 DNS 记录（全量查询，仅此一次）…")
            all_records = self.get_dns_records()
            logger.info(f"当前共有 {len(all_records)} 条 DNS 记录")

            # ── 步骤 2：批量清理所有目标域名的旧记录 ─────────────────────
            target_domains = {h["domain"] for h in valid_hosts}
            if all_records:
                logger.info(f"正在清理 {len(target_domains)} 个域名的旧记录…")
                self._batch_cleanup_domains(target_domains, all_records)
            else:
                logger.info("当前无旧记录，跳过清理步骤")

            # ── 步骤 3：顺序添加所有新记录 ───────────────────────────────
            success_count = 0
            for host in valid_hosts:
                try:
                    if self._add_dns_record_direct(host["domain"], host["ip"]):
                        success_count += 1
                except Exception:
                    logger.error(f"添加 DNS 记录异常：{host.get('domain')}")

            self._last_sync_success = success_count > 0

            if self._last_sync_success:
                logger.info(f"DNS 同步完成：成功 {success_count}/{len(valid_hosts)} 条记录")
            else:
                logger.error("DNS 同步失败：没有成功添加任何记录")

            return self._last_sync_success

        except httpx.ConnectError:
            logger.error("同步 hosts 到爱快 DNS 时发生错误：无法连接到爱快路由器")
            return False
        except Exception:
            logger.error("同步 hosts 到爱快 DNS 时发生错误")
            return False

    def get_last_sync_status(self) -> bool:
        """获取最后一次同步是否成功"""
        return self._last_sync_success

    def delete_dns_record(self, record_id: str | int) -> bool:
        """
        删除单条 DNS 记录（公共接口）。

        Args:
            record_id: DNS 记录 ID

        Returns:
            bool: 操作是否成功
        """
        return self._delete_dns_record(str(record_id))

    # ─────────────────────── DNS 记录启用 / 停用 ────────────────────────

    def enable_dns_record(self, record_id: str | int) -> bool:
        """
        启用指定 DNS 记录。

        iKuai API：action=up, param={"id": "<string>"}
        注意：id 必须为字符串类型（HAR 中确认）。

        Args:
            record_id: DNS 记录 ID

        Returns:
            bool: 操作是否成功
        """
        return self._toggle_dns_record(str(record_id), enable=True)

    def disable_dns_record(self, record_id: str | int) -> bool:
        """
        停用指定 DNS 记录。

        iKuai API：action=down, param={"id": "<string>"}

        Args:
            record_id: DNS 记录 ID

        Returns:
            bool: 操作是否成功
        """
        return self._toggle_dns_record(str(record_id), enable=False)

    def _toggle_dns_record(self, record_id: str, enable: bool) -> bool:
        """
        切换 DNS 记录的启用/停用状态（内部实现）。

        Args:
            record_id: 字符串格式的记录 ID
            enable: True=启用(up)，False=停用(down)

        Returns:
            bool: 操作是否成功
        """
        if not self.login():
            return False

        if not self._session:
            return False

        action = "up" if enable else "down"
        action_label = "启用" if enable else "停用"

        try:
            url = f"{self._base_url}/Action/call"
            payload = {
                "func_name": "dns",
                "action": action,
                "param": {
                    "id": record_id,  # 必须是字符串
                },
            }

            resp = self._session.post(url, json=payload, headers=self._get_headers())
            if resp.status_code == 200:
                result = resp.json()
                if _is_ikuai_success(result):
                    logger.info(f"成功{action_label} DNS 记录：ID={record_id}")
                    return True
                else:
                    logger.error(f"{action_label} DNS 记录失败：ID={record_id}, 响应={result}")
                    return False
            logger.error(f"{action_label} DNS 记录请求失败，状态码：{resp.status_code}")
            return False

        except httpx.ConnectError:
            logger.error(f"{action_label} DNS 记录异常：无法连接到爱快路由器")
            return False
        except Exception:
            logger.error(f"{action_label} DNS 记录异常：请求失败")
            return False

    # ─────────────────────── DNS 配置导出 / 导入 ────────────────────────

    def export_dns_txt(self) -> bytes | None:
        """
        导出所有 DNS 记录为 TXT 文件（二进制内容）。

        iKuai API 两步走：
          1. POST /Action/call  {"func_name":"dns","action":"EXPORT","param":{"format":"txt"}}
             → 响应含 Filename 字段
          2. GET  /Action/download?filename=<Filename>
             → 返回文件内容

        Returns:
            bytes | None: 文件内容，失败返回 None
        """
        if not self.login():
            return None

        if not self._session:
            return None

        try:
            # 步骤 1：触发导出，获取服务器生成的文件名
            url = f"{self._base_url}/Action/call"
            payload = {
                "func_name": "dns",
                "action": "EXPORT",
                "param": {"format": "txt"},
            }

            resp = self._session.post(url, json=payload, headers=self._get_headers())
            if resp.status_code != 200:
                logger.error(f"DNS 导出请求失败，状态码：{resp.status_code}")
                return None

            result = resp.json()
            if not _is_ikuai_success(result):
                logger.error(f"DNS 导出失败：{result}")
                return None

            filename = result.get("Filename") or result.get("filename")
            if not filename:
                logger.error(f"DNS 导出响应中缺少 Filename 字段：{result}")
                return None

            # 步骤 2：下载文件
            logger.info(f"正在下载 DNS 导出文件：{filename}")
            content = self._download_file(filename)
            if content is not None:
                logger.info(f"DNS 导出成功，文件大小：{len(content)} 字节")
            return content

        except httpx.ConnectError:
            logger.error("DNS 导出异常：无法连接到爱快路由器")
            return None
        except Exception:
            logger.error("DNS 导出异常：请求失败")
            return None

    def import_dns_txt(self, content: bytes, append: bool = False) -> bool:
        """
        从 TXT 文件内容导入 DNS 记录。

        iKuai API 两步走：
          1. POST /Action/upload  上传文件，得到服务器保存的文件名
          2. POST /Action/call    {"func_name":"dns","action":"IMPORT","param":{"filename":"xxx","append":0/1}}

        Args:
            content: DNS 配置文件的二进制内容
            append: False=覆盖现有记录，True=追加到现有记录

        Returns:
            bool: 导入是否成功
        """
        if not self.login():
            return False

        if not self._session:
            return False

        try:
            # 步骤 1：上传文件
            upload_url = f"{self._base_url}/Action/upload"
            files = {"file": ("dns.txt", content, "text/plain")}

            upload_resp = self._session.post(upload_url, files=files)
            if upload_resp.status_code != 200:
                logger.error(f"DNS 导入文件上传失败，状态码：{upload_resp.status_code}")
                return False

            upload_result = upload_resp.json()
            # 从上传响应中取服务器保存的文件名；部分固件直接返回 "dns.txt"
            server_filename = (
                upload_result.get("Filename")
                or upload_result.get("filename")
                or "dns.txt"
            )

            # 步骤 2：触发导入
            url = f"{self._base_url}/Action/call"
            payload = {
                "func_name": "dns",
                "action": "IMPORT",
                "param": {
                    "filename": server_filename,
                    "append": 1 if append else 0,
                },
            }

            resp = self._session.post(url, json=payload, headers=self._get_headers())
            if resp.status_code != 200:
                logger.error(f"DNS 导入请求失败，状态码：{resp.status_code}")
                return False

            result = resp.json()
            if _is_ikuai_success(result):
                mode = "追加" if append else "覆盖"
                logger.info(f"DNS 导入成功（{mode}模式）")
                return True
            else:
                logger.error(f"DNS 导入失败：{result}")
                return False

        except httpx.ConnectError:
            logger.error("DNS 导入异常：无法连接到爱快路由器")
            return False
        except Exception:
            logger.error("DNS 导入异常：请求失败")
            return False

    # ─────────────────────── 备份文件下载 ───────────────────────────────

    def export_backup(self, backup_filename: str) -> bytes | None:
        """
        下载指定备份文件。

        iKuai API 两步走：
          1. POST /Action/call  {"func_name":"backup","action":"EXPORT","param":{"srcfile":"xxx.bak"}}
             → 响应含 Filename 字段
          2. GET  /Action/download?filename=<Filename>
             → 返回文件内容

        Args:
            backup_filename: 备份文件名，例如 "2026-04-28-173102.bak"

        Returns:
            bytes | None: 文件内容，失败返回 None
        """
        if not self.login():
            return None

        if not self._session:
            return None

        try:
            # 步骤 1：触发备份导出
            url = f"{self._base_url}/Action/call"
            payload = {
                "func_name": "backup",
                "action": "EXPORT",
                "param": {"srcfile": backup_filename},
            }

            resp = self._session.post(url, json=payload, headers=self._get_headers())
            if resp.status_code != 200:
                logger.error(f"备份导出请求失败，状态码：{resp.status_code}")
                return None

            result = resp.json()
            if not _is_ikuai_success(result):
                logger.error(f"备份导出失败：{result}")
                return None

            filename = result.get("Filename") or result.get("filename") or backup_filename

            # 步骤 2：下载文件
            logger.info(f"正在下载备份文件：{filename}")
            content = self._download_file(filename)
            if content is not None:
                logger.info(f"备份文件下载成功，文件大小：{len(content)} 字节")
            return content

        except httpx.ConnectError:
            logger.error("备份导出异常：无法连接到爱快路由器")
            return None
        except Exception:
            logger.error("备份导出异常：请求失败")
            return None

    # ─────────────────────── 通用文件下载 ───────────────────────────────

    def _download_file(self, filename: str) -> bytes | None:
        """
        通过 /Action/download?filename=<filename> 下载爱快服务器上的文件。

        用于：DNS 配置 TXT 文件导出、备份文件下载等。

        Args:
            filename: 服务器上的文件名（由对应 EXPORT API 响应中的 Filename 字段提供）

        Returns:
            bytes | None: 文件内容，失败返回 None
        """
        if not self._session:
            return None

        try:
            url = f"{self._base_url}/Action/download"
            resp = self._session.get(
                url,
                params={"filename": filename},
                headers=self._get_headers(),
            )

            if resp.status_code == 200:
                return resp.content
            else:
                logger.error(f"文件下载失败，状态码：{resp.status_code}，文件名：{filename}")
                return None

        except httpx.ConnectError:
            logger.error(f"文件下载异常：无法连接到爱快路由器（filename={filename}）")
            return None
        except Exception:
            logger.error(f"文件下载异常：请求失败（filename={filename}）")
            return None

    def close(self):
        """关闭会话"""
        if self._session:
            self._session.close()
            self._session = None
