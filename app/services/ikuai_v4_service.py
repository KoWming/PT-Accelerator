"""iKuai 4.0 DNS proxy rules, authenticated with an API Bearer token."""
import ipaddress
from urllib.parse import quote, urlparse

import httpx

from app.services.ikuai_service import IkuaiService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IkuaiV4Service(IkuaiService):
    RULES = "/api/v4.0/network/dns/proxy/rules"
    COMMENT = "PT-Accelerator"

    def __init__(self, host: str, token: str, verify_tls: bool = True):
        super().__init__()
        if "://" not in host:
            host = "https://" + host
        parsed = urlparse(host)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("爱快 4.0 需要 HTTPS 管理地址")
        self._base_url = host.rstrip("/")
        self._token = token
        self.last_sync_error = ""
        self._session = httpx.Client(
            base_url=self._base_url, timeout=15, verify=verify_tls,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        )

    @property
    def is_enabled(self) -> bool:
        return bool(self._token)

    def _request(self, method: str, path: str, **kwargs):
        response = self._session.request(method, path, **kwargs)
        response.raise_for_status()
        result = response.json()
        if result.get("code") != 0:
            # Never include the request headers or response body in errors.
            raise ValueError(f"爱快 API 请求失败（code={result.get('code')}）")
        return result

    def test_connection(self) -> tuple[bool, str]:
        if not self._token:
            return False, "未配置 API Token"
        try:
            self._request("GET", self.RULES, params={"page": 1, "page_size": 1})
            return True, "爱快 4.0 API 连接成功"
        except httpx.HTTPStatusError as exc:
            return False, f"爱快 API 返回 HTTP {exc.response.status_code}，请检查 Token 权限"
        except Exception:
            return False, "爱快 API 连接失败，请检查地址、Token 和 HTTPS 证书信任设置"

    def get_dns_records(self) -> list:
        records = []
        seen_ids = set()
        for page in range(1, 10001):
            # Some firmware only honors numeric `limit`, ignoring page/page_size.
            result = self._request("GET", self.RULES, params={"page": page, "page_size": 100, "limit": 100})
            payload = result.get("results", result.get("data"))
            if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
                raise ValueError("爱快 DNS 规则响应格式不正确")
            batch = payload["data"]
            total = payload.get("total")
            batch_ids = {str(row["id"]) for row in batch}
            if len(batch_ids) != len(batch):
                raise ValueError("爱快 DNS 接口返回重复的记录 ID")
            if seen_ids.intersection(batch_ids):
                # Repeated pages are not duplicate DNS rules. Retry a full snapshot
                # using the firmware's supported limit, then verify completeness.
                if total is None:
                    raise ValueError("爱快 DNS 接口重复返回同一页，无法读取完整规则")
                result = self._request("GET", self.RULES, params={"limit": max(100, int(total))})
                snapshot = result.get("results", result.get("data"))
                if not isinstance(snapshot, dict) or not isinstance(snapshot.get("data"), list):
                    raise ValueError("爱快 DNS 规则响应格式不正确")
                rows = snapshot["data"]
                expected = int(snapshot.get("total", total))
                if len(rows) < expected or len({str(row["id"]) for row in rows}) != len(rows):
                    raise ValueError("爱快 DNS 接口未返回完整规则，请检查固件的分页支持")
                return rows
            records.extend(batch)
            seen_ids.update(batch_ids)
            if total is not None and len(records) >= int(total):
                return records
            if not batch:
                if total is not None:
                    raise ValueError("爱快 DNS 规则读取不完整，已停止同步")
                return records
            if total is None and len(batch) < 100:
                return records
        raise ValueError("爱快 DNS 规则分页超过限制")

    def _write_rule(self, domain: str, ip: str, record: dict | None = None):
        address = ipaddress.ip_address(ip)
        body = {
            "domain": domain, "dns_addr": str(address),
            "parse_type": "ipv4" if address.version == 4 else "ipv6",
            "is_ipv6": 0 if address.version == 4 else 1,
            "enabled": "yes", "src_addr": "", "comment": self.COMMENT,
        }
        if record is not None:
            self._request("PUT", self.RULES + "/" + quote(str(record["id"]), safe=""), json=body)
        else:
            self._request("POST", self.RULES, json=body)

    def sync_hosts_to_dns(self, hosts: list[dict]) -> bool:
        self._last_sync_success = False
        self.last_sync_error = ""
        try:
            # Validate all desired records before writing anything.
            desired = {}
            for host in hosts:
                domain = str(host["domain"]).strip().lower().rstrip(".")
                if not domain or "/" in domain or "*" in domain:
                    raise ValueError("需要精确域名")
                try:
                    ip = str(ipaddress.ip_address(host["ip"]))
                except ValueError:
                    raise ValueError("目标 IP 地址无效") from None
                if domain in desired and desired[domain] != ip:
                    raise ValueError("同一域名存在不同的目标 IP")
                desired[domain] = ip
            if not desired:
                self.last_sync_error = "没有需要同步的有效域名"
                return False
            records = self.get_dns_records()  # Failure aborts; never treat it as an empty list.
            plan = []
            for domain, ip in desired.items():
                matches = [r for r in records if str(r.get("domain", "")).lower().rstrip(".") == domain]
                if any(r.get("comment") != self.COMMENT for r in matches) or len(matches) > 1:
                    raise ValueError("目标域名已有其他规则，请先处理冲突")
                record = matches[0] if matches else None
                if record and str(record.get("dns_addr")) == ip and record.get("enabled") in (True, 1, "1", "yes"):
                    continue
                plan.append((domain, ip, record))
            for domain, ip, record in plan:
                self._write_rule(domain, ip, record)
            actual = self.get_dns_records()
            self._last_sync_success = all(any(
                r.get("domain") == domain and r.get("dns_addr") == ip
                and r.get("comment") == self.COMMENT and r.get("enabled") in (True, 1, "1", "yes")
                for r in actual
            ) for domain, ip in desired.items())
            if not self._last_sync_success:
                self.last_sync_error = "写入后回读结果不一致，请重试同步"
        except Exception as exc:
            if isinstance(exc, httpx.HTTPStatusError):
                self.last_sync_error = f"爱快 API 返回 HTTP {exc.response.status_code}"
            elif isinstance(exc, ValueError):
                self.last_sync_error = str(exc)
            else:
                self.last_sync_error = "爱快 API 请求失败，请检查连接、Token 和 HTTPS 证书"
            logger.warning("爱快 4.0 DNS 同步失败：%s", self.last_sync_error)
            self._last_sync_success = False
        return self._last_sync_success

    def add_dns_record(self, domain: str, ip: str, comment: str = "PT-Accelerator") -> bool:
        return self.sync_hosts_to_dns([{"domain": domain, "ip": ip}])

    def delete_dns_record(self, record_id: str | int) -> bool:
        try:
            self._request("DELETE", self.RULES + "/" + quote(str(record_id), safe=""))
            return True
        except Exception:
            return False

    def _toggle_dns_record(self, record_id: str, enable: bool) -> bool:
        try:
            record = next(r for r in self.get_dns_records() if str(r["id"]) == str(record_id))
            body = {key: record[key] for key in ("domain", "dns_addr", "parse_type", "is_ipv6", "src_addr", "comment") if key in record}
            body["enabled"] = "yes" if enable else "no"
            self._request("PUT", self.RULES + "/" + quote(str(record_id), safe=""), json=body)
            return True
        except Exception:
            return False

    def export_dns_txt(self) -> bytes | None:
        # The legacy router TXT import/export format has no documented v4 equivalent.
        return None

    def import_dns_txt(self, content: bytes, append: bool = False) -> bool:
        return False


def create_ikuai_service(*, host: str, port=None, username="admin", password="",
                         api_version="legacy", token="", verify_tls=True) -> IkuaiService:
    if api_version == "v4":
        return IkuaiV4Service(host, token, verify_tls)
    if api_version != "legacy":
        raise ValueError("不支持的爱快 API 版本")
    service = IkuaiService()
    service.init_config(host=host, port=port, username=username, password=password)
    return service
