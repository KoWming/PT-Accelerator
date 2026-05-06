"""
Cloudflare 域名检测服务。

当前实现：
- 白名单判定
- 主域名白名单判定
- DNS 解析 + Cloudflare IP 段判定
- CNAME 检测
- HTTP 响应头/正文检测
- 多 DNS 解析兜底
- 内存缓存
"""
from __future__ import annotations

import concurrent.futures
import ipaddress
import socket
import time
from urllib.parse import urlparse

import httpx

from app.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)

CACHE_EXPIRY_SECONDS = 3600
HTTP_DETECT_TIMEOUT_SECONDS = 3
CLOUDFLARE_IP_RANGES = [
    "103.21.244.0/22",
    "103.22.200.0/22",
    "103.31.4.0/22",
    "104.16.0.0/13",
    "104.24.0.0/14",
    "108.162.192.0/18",
    "131.0.72.0/22",
    "141.101.64.0/18",
    "162.158.0.0/15",
    "172.64.0.0/13",
    "173.245.48.0/20",
    "188.114.96.0/20",
    "190.93.240.0/20",
    "197.234.240.0/22",
    "198.41.128.0/17",
    "2400:cb00::/32",
    "2405:8100::/32",
    "2405:b500::/32",
    "2606:4700::/32",
    "2803:f800::/32",
    "2a06:98c0::/29",
    "2c0f:f248::/32",
]
CLOUDFLARE_NETWORKS = tuple(ipaddress.ip_network(item) for item in CLOUDFLARE_IP_RANGES)
CLOUDFLARE_HEADER_NAMES = (
    "cf-ray",
    "cf-cache-status",
    "cf-request-id",
    "cf-worker",
    "cf-connecting-ip",
    "cf-visitor",
    "cf-bgj",
    "cf-ipcountry",
    "cf-apo-via",
    "cf-edge-cache",
)
CLOUDFLARE_COOKIE_MARKERS = (
    "__cfduid",
    "cf_clearance",
    "cf_use_ob",
)
CLOUDFLARE_CNAME_MARKERS = (
    "cloudflare",
    "workers.dev",
    "pages.dev",
)
CLOUDFLARE_CONTENT_MARKERS = (
    "cloudflare",
    "cdn-cgi",
    "cloudflare-nginx",
    "__cf_email__",
    "cf-error-code",
    "cf_chl_",
)
PUBLIC_DNS_SERVERS = ("8.8.8.8", "1.1.1.1", "9.9.9.9", "208.67.222.222")
DEFAULT_HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "close",
}


class CloudflareDetector:
    """Cloudflare 域名检测器。"""

    def __init__(self):
        self._cache: dict[str, dict] = {}

    def detect(self, value: str) -> dict:
        """检测域名是否使用 Cloudflare。"""
        domain = self._normalize_domain(value)
        checked_at = time.strftime("%Y-%m-%dT%H:%M:%S")
        default_result = {
            "domain": domain,
            "is_cloudflare": False,
            "source": "none",
            "resolved_ips": [],
            "cached": False,
            "checked_at": checked_at,
        }
        if not domain:
            return default_result

        cached = self._get_cached(domain)
        if cached:
            result = cached.copy()
            result["cached"] = True
            return result

        whitelist = self._get_whitelist()
        if domain in whitelist:
            result = {
                **default_result,
                "is_cloudflare": True,
                "source": "whitelist",
            }
            self._cache_result(result)
            return result.copy()

        main_domain = self._get_main_domain(domain)
        if main_domain and main_domain in whitelist:
            result = {
                **default_result,
                "is_cloudflare": True,
                "source": "main_domain_whitelist",
            }
            self._cache_result(result)
            return result.copy()

        resolved_ips = self._resolve_ips(domain)
        if any(self._is_cloudflare_ip(ip) for ip in resolved_ips):
            result = {
                **default_result,
                "is_cloudflare": True,
                "source": "dns_ip_range",
                "resolved_ips": resolved_ips,
            }
            self._cache_result(result)
            return result.copy()

        cname_result = self._check_cloudflare_by_cname(domain)
        if cname_result:
            result = {
                **default_result,
                "is_cloudflare": True,
                "source": "dns_cname",
                "resolved_ips": resolved_ips,
            }
            self._cache_result(result)
            return result.copy()

        http_result = self._check_cloudflare_by_http(domain)
        if http_result:
            result = {
                **default_result,
                "is_cloudflare": True,
                "source": http_result,
                "resolved_ips": resolved_ips,
            }
            self._cache_result(result)
            return result.copy()

        multi_dns_ips = self._resolve_ips_with_public_dns(domain)
        merged_ips = self._merge_unique_ips(resolved_ips, multi_dns_ips)
        if any(self._is_cloudflare_ip(ip) for ip in merged_ips):
            result = {
                **default_result,
                "is_cloudflare": True,
                "source": "multi_dns_ip_range",
                "resolved_ips": merged_ips,
            }
            self._cache_result(result)
            return result.copy()

        result = {
            **default_result,
            "resolved_ips": merged_ips,
        }
        self._cache_result(result)
        return result.copy()

    def is_cloudflare_domain(self, value: str) -> bool:
        """仅返回布尔判断结果。"""
        return bool(self.detect(value)["is_cloudflare"])

    def _get_cached(self, domain: str) -> dict | None:
        cached = self._cache.get(domain)
        if not cached:
            return None
        if time.time() - cached["_cached_at"] >= CACHE_EXPIRY_SECONDS:
            self._cache.pop(domain, None)
            return None
        result = cached.copy()
        result.pop("_cached_at", None)
        return result

    def _cache_result(self, result: dict):
        payload = result.copy()
        payload["_cached_at"] = time.time()
        self._cache[result["domain"]] = payload
        if len(self._cache) > 1000:
            self._clean_expired_cache()

    def _clean_expired_cache(self):
        now = time.time()
        expired_keys = [
            key for key, value in self._cache.items()
            if now - value.get("_cached_at", 0) >= CACHE_EXPIRY_SECONDS
        ]
        for key in expired_keys:
            self._cache.pop(key, None)

    @staticmethod
    def _normalize_domain(value: str) -> str:
        value = (value or "").strip().lower()
        if not value:
            return ""
        if "://" in value:
            parsed = urlparse(value)
            hostname = (parsed.hostname or "").strip().lower().rstrip(".")
            if not hostname:
                return ""
            if parsed.port:
                return f"{hostname}:{parsed.port}"
            return hostname
        cleaned = value.split("/", 1)[0].strip().lower().rstrip(".")
        if cleaned.startswith("[") and "]" in cleaned:
            cleaned = cleaned[1:].split("]", 1)[0]
        return cleaned

    @staticmethod
    def _get_main_domain(domain: str) -> str:
        host = CloudflareDetector._domain_without_port(domain)
        parts = host.split(".")
        if len(parts) <= 2:
            return host
        country_tlds = {"uk", "au", "jp", "cn", "br", "mx", "ru", "eu", "de", "fr", "it", "nl", "sg", "kr"}
        if len(parts) >= 3 and parts[-2] in country_tlds:
            return ".".join(parts[-3:])
        return ".".join(parts[-2:])

    @staticmethod
    def _get_whitelist() -> set[str]:
        configured = config.get("cloudflare_domains", default=[])
        if isinstance(configured, str):
            configured = [configured]
        normalized_items = {
            CloudflareDetector._normalize_domain(item)
            for item in configured
            if CloudflareDetector._normalize_domain(item)
        }
        result = set(normalized_items)
        for item in normalized_items:
            result.add(CloudflareDetector._domain_without_port(item))
        return result

    @staticmethod
    def _resolve_ips(domain: str) -> list[str]:
        host = CloudflareDetector._domain_without_port(domain)
        try:
            infos = socket.getaddrinfo(host, None)
        except socket.gaierror as e:
            logger.debug(f"Cloudflare 域名解析失败：{host}，错误：{e}")
            return []

        ips: list[str] = []
        for info in infos:
            address = info[4][0]
            if address not in ips:
                ips.append(address)
        return ips

    def _check_cloudflare_by_cname(self, domain: str) -> bool:
        host = self._domain_without_port(domain)
        try:
            import dns.exception
            import dns.resolver
        except ImportError:
            logger.debug("Cloudflare CNAME 检测跳过：dnspython 未安装")
            return False

        try:
            resolver = dns.resolver.Resolver(configure=True)
            resolver.timeout = 2.0
            resolver.lifetime = 2.0
            answers = resolver.resolve(host, "CNAME")
            for rdata in answers:
                cname = str(rdata.target).lower().rstrip(".")
                if any(marker in cname for marker in CLOUDFLARE_CNAME_MARKERS):
                    return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout, dns.exception.DNSException) as e:
            logger.debug(f"Cloudflare CNAME 检测失败：{host}，错误：{e}")
        return False

    def _check_cloudflare_by_http(self, domain: str) -> str | None:
        host = self._domain_without_port(domain)
        for scheme in ("https", "http"):
            url = f"{scheme}://{host}"
            try:
                with httpx.Client(timeout=HTTP_DETECT_TIMEOUT_SECONDS, verify=False, headers=DEFAULT_HTTP_HEADERS, follow_redirects=True) as client:
                    head_response = client.head(url)
                    if self._response_has_cloudflare_markers(head_response.headers):
                        return "http_headers"

                    get_response = client.get(url)
                    if self._response_has_cloudflare_markers(get_response.headers):
                        return "http_headers"
                    if self._response_content_has_cloudflare_markers(get_response.text):
                        return "http_content"
            except Exception as e:
                logger.debug(f"Cloudflare HTTP 检测失败：{url}，错误：{e}")
        return None

    def _resolve_ips_with_public_dns(self, domain: str) -> list[str]:
        host = self._domain_without_port(domain)
        try:
            import dns.resolver
        except ImportError:
            logger.debug("Cloudflare 多 DNS 检测跳过：dnspython 未安装")
            return []

        def resolve_with_server(server: str) -> list[str]:
            try:
                resolver = dns.resolver.Resolver(configure=False)
                resolver.nameservers = [server]
                resolver.timeout = 1.5
                resolver.lifetime = 1.5
                answers = resolver.resolve(host, "A")
                return [str(rdata) for rdata in answers]
            except Exception as e:
                logger.debug(f"Cloudflare 多 DNS 检测失败：{host}@{server}，错误：{e}")
                return []

        ips: list[str] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(PUBLIC_DNS_SERVERS)) as executor:
            for result in executor.map(resolve_with_server, PUBLIC_DNS_SERVERS):
                ips = self._merge_unique_ips(ips, result)
        return ips

    @staticmethod
    def _response_has_cloudflare_markers(headers: httpx.Headers) -> bool:
        normalized_headers = {key.lower(): value for key, value in headers.items()}
        if any(header in normalized_headers for header in CLOUDFLARE_HEADER_NAMES):
            return True

        server = normalized_headers.get("server", "").lower()
        if "cloudflare" in server:
            return True

        cookies = normalized_headers.get("set-cookie", "").lower()
        return any(marker in cookies for marker in CLOUDFLARE_COOKIE_MARKERS)

    @staticmethod
    def _response_content_has_cloudflare_markers(content: str) -> bool:
        normalized_content = (content or "").lower()
        return any(marker in normalized_content for marker in CLOUDFLARE_CONTENT_MARKERS)

    @staticmethod
    def _domain_without_port(domain: str) -> str:
        value = (domain or "").strip().lower()
        if not value:
            return ""
        if value.startswith("[") and "]" in value:
            host, _, remainder = value[1:].partition("]")
            return host if remainder.startswith(":") or not remainder else value
        if value.count(":") == 1 and "." in value:
            host, _, port = value.rpartition(":")
            if port.isdigit():
                return host
        return value

    @staticmethod
    def _merge_unique_ips(*groups: list[str]) -> list[str]:
        merged: list[str] = []
        for group in groups:
            for ip in group:
                if ip not in merged:
                    merged.append(ip)
        return merged

    @staticmethod
    def _is_cloudflare_ip(ip: str) -> bool:
        try:
            ip_obj = ipaddress.ip_address(ip)
        except ValueError:
            return False
        return any(ip_obj in network for network in CLOUDFLARE_NETWORKS)


cloudflare_detector = CloudflareDetector()

