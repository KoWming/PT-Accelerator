"""
备份服务

备份配置存储在 config.backup，本地备份文件存储在 cache/backups。
"""
import hashlib
import os
import shutil
import zipfile
import httpx
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Optional
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET

from app.utils.logger import get_logger
from app.utils.secret_crypto import encrypt_secret, decrypt_secret

logger = get_logger(__name__)

# 默认备份文件列表
DEFAULT_BACKUP_FILES = [
    "config/config.yaml",
]


class BackupService:
    """备份服务"""

    def __init__(self):
        self._backup_dir = "cache/backups"

    def _get_config(self) -> dict:
        """获取备份配置"""
        from app.config import config
        return config.get("backup", default={})

    def _save_config(self, config_dict: dict):
        """保存备份配置"""
        from app.config import config
        config.set("backup", config_dict)
        config.save()

    def _build_backup_record(
        self,
        *,
        source: str,
        file_name: str,
        size: int = 0,
        created_at: str = "",
        file_path: str = "",
    ) -> dict:
        backup_id = hashlib.md5(f"{source}:{file_name}".encode("utf-8")).hexdigest()[:8]
        record = {
            "id": backup_id,
            "file": file_name,
            "size": int(size or 0),
            "created_at": created_at,
            "source": source,
        }
        if file_path:
            record["file_path"] = file_path
        return record

    def _parse_backup_filename_time(self, file_name: str) -> str:
        stem = Path(file_name).stem
        if not stem.startswith("backup_"):
            return ""

        raw = stem.removeprefix("backup_")
        try:
            return datetime.strptime(raw, "%Y%m%d_%H%M%S").isoformat()
        except ValueError:
            return ""

    def _normalize_backup_time(self, value: Optional[str], fallback: str = "") -> str:
        if not value:
            return fallback

        text = value.strip()
        if not text:
            return fallback

        try:
            return parsedate_to_datetime(text).isoformat()
        except Exception:
            return fallback

    def _list_local_backups(self) -> list[dict]:
        """扫描本地备份目录。"""
        backup_dir = Path(self._backup_dir)
        if not backup_dir.exists():
            return []

        backups: list[dict] = []
        for file in sorted(backup_dir.glob("*.zip"), reverse=True):
            try:
                stat = file.stat()
                created_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
                backups.append(
                    self._build_backup_record(
                        source="local",
                        file_name=file.name,
                        size=stat.st_size,
                        created_at=created_at,
                        file_path=str(file),
                    )
                )
            except OSError as e:
                logger.warning(f"读取本地备份文件失败: {file} - {e}")
        return backups

    def _build_remote_file_url(self, webdav_url: str, webdav_path: str, file_name: str) -> str:
        return f"{webdav_url.rstrip('/')}{webdav_path.rstrip('/')}/{file_name}"

    def _list_remote_backups(self) -> list[dict]:
        """列出 WebDAV 远程备份文件。"""
        cfg = self._get_config()
        if not cfg.get("webdav_enabled"):
            return []

        webdav_url = (cfg.get("webdav_url") or "").strip().rstrip("/")
        webdav_user = cfg.get("webdav_username", "")
        webdav_pass = decrypt_secret(cfg.get("webdav_password", ""))  # 解密
        webdav_path = (cfg.get("webdav_path") or "/backups").strip() or "/backups"
        auth = (webdav_user, webdav_pass) if webdav_user else None

        if not webdav_url:
            return []

        directory_url = f"{webdav_url}{webdav_path.rstrip('/')}/"
        headers = {
            "Depth": "1",
            "Content-Type": "application/xml; charset=utf-8",
        }
        body = """<?xml version="1.0" encoding="utf-8" ?>
<d:propfind xmlns:d="DAV:">
  <d:prop>
    <d:displayname />
    <d:getcontentlength />
    <d:getlastmodified />
    <d:resourcetype />
  </d:prop>
</d:propfind>
"""

        try:
            with httpx.Client(timeout=30, follow_redirects=True) as client:
                response = client.request("PROPFIND", directory_url, headers=headers, content=body.encode("utf-8"), auth=auth)

            if response.status_code in (401, 403):
                logger.warning("列出 WebDAV 远程备份失败：认证失败或无权限")
                return []
            if response.status_code == 404:
                logger.info(f"WebDAV 远程备份目录不存在: {directory_url}")
                return []
            if response.status_code not in (200, 207):
                logger.warning(f"列出 WebDAV 远程备份失败: HTTP {response.status_code}")
                return []

            root = ET.fromstring(response.text)
            ns = {"d": "DAV:"}
            backups: list[dict] = []

            for item in root.findall("d:response", ns):
                href = item.findtext("d:href", default="", namespaces=ns)
                prop = item.find("d:propstat/d:prop", ns)
                if prop is None:
                    continue

                resource_type = prop.find("d:resourcetype", ns)
                if resource_type is not None and resource_type.find("d:collection", ns) is not None:
                    continue

                display_name = prop.findtext("d:displayname", default="", namespaces=ns).strip()
                parsed_path = unquote(urlparse(href).path)
                file_name = display_name or Path(parsed_path).name
                if not file_name or not file_name.lower().endswith(".zip"):
                    continue

                size_text = prop.findtext("d:getcontentlength", default="0", namespaces=ns).strip()
                modified_text = prop.findtext("d:getlastmodified", default="", namespaces=ns)
                fallback_time = self._parse_backup_filename_time(file_name)
                created_at = self._normalize_backup_time(modified_text, fallback=fallback_time)

                try:
                    size = int(size_text or 0)
                except ValueError:
                    size = 0

                backups.append(
                    self._build_backup_record(
                        source="remote",
                        file_name=file_name,
                        size=size,
                        created_at=created_at,
                    )
                )

            return backups
        except Exception as e:
            logger.warning(f"列出 WebDAV 远程备份失败: {e}")
            return []

    def get_config(self) -> dict:
        """获取备份配置（密码脱敏）"""
        cfg = self._get_config()
        webdav_password = cfg.get("webdav_password", "")
        return {
            "webdav_enabled": cfg.get("webdav_enabled", False),
            "webdav_url": cfg.get("webdav_url", ""),
            "webdav_username": cfg.get("webdav_username", ""),
            "webdav_password": "********" if webdav_password else "",
            "webdav_path": cfg.get("webdav_path", "/backups"),
            "local_keep_count": cfg.get("local_keep_count", 7),
        }

    def update_config(
        self,
        webdav_enabled: Optional[bool] = None,
        webdav_url: Optional[str] = None,
        webdav_username: Optional[str] = None,
        webdav_password: Optional[str] = None,
        webdav_path: Optional[str] = None,
        local_keep_count: Optional[int] = None,
    ) -> dict:
        """
        更新备份配置（只更新提供的字段）

        Returns:
            更新后的配置（密码脱敏）
        """
        cfg = self._get_config()

        if webdav_enabled is not None:
            cfg["webdav_enabled"] = webdav_enabled
        if webdav_url is not None and webdav_url != "":
            cfg["webdav_url"] = webdav_url.strip().rstrip("/")
        if webdav_username is not None:
            cfg["webdav_username"] = webdav_username
        if webdav_password is not None and webdav_password != "":
            cfg["webdav_password"] = encrypt_secret(webdav_password)  # 加密后存储
        if webdav_path is not None and webdav_path != "":
            cfg["webdav_path"] = webdav_path.strip()
        if local_keep_count is not None:
            cfg["local_keep_count"] = max(1, min(30, local_keep_count))

        self._save_config(cfg)
        logger.info("备份配置已更新")
        return self.get_config()

    def list_backups(self) -> list[dict]:
        """列出本地与远程备份。"""
        backups = self._list_local_backups()
        backups.extend(self._list_remote_backups())
        backups.sort(key=lambda item: (item.get("created_at") or "", item.get("file") or ""), reverse=True)
        return backups

    def _find_backup(self, backup_id: str) -> Optional[dict]:
        for backup in self.list_backups():
            if backup.get("id") == backup_id:
                return backup
        return None

    def _find_local_backup(self, backup_id: str) -> Optional[dict]:
        for backup in self._list_local_backups():
            if backup.get("id") == backup_id:
                return backup
        return None

    def create_backup(self, description: str = "") -> dict:
        """
        创建本地备份

        Returns:
            {"backup_id": str, "file_path": str, "message": str}
        """
        _ = description

        files = self._collect_files()
        if not files:
            raise ValueError("没有找到需要备份的文件")

        zip_path = self._package_files(files)
        backup_record = self._build_backup_record(
            source="local",
            file_name=os.path.basename(zip_path),
            size=os.path.getsize(zip_path),
            created_at=datetime.now().isoformat(),
            file_path=zip_path,
        )

        cfg = self._get_config()
        keep_count = cfg.get("local_keep_count", 7)
        self._cleanup_old_backups(keep_count)
        logger.info(f"本地备份已创建: {backup_record['id']}")

        return {
            "backup_id": backup_record["id"],
            "file_path": zip_path,
            "message": "备份已创建",
        }

    async def test_webdav_connection(
        self,
        webdav_url: str,
        webdav_username: str = "",
        webdav_password: str = "",
        webdav_path: str = "/backups",
    ) -> dict:
        """测试 WebDAV 连通性和写权限，不落盘配置。"""
        webdav_url = (webdav_url or "").strip().rstrip("/")
        webdav_path = (webdav_path or "/backups").strip() or "/backups"

        if not webdav_url:
            return {"success": False, "message": "WebDAV URL 未配置"}
        if not webdav_url.startswith(("http://", "https://")):
            return {"success": False, "message": "WebDAV URL 格式无效，必须以 http:// 或 https:// 开头"}

        test_file_name = f".pt-accelerator-webdav-test-{datetime.now().strftime('%Y%m%d%H%M%S')}.tmp"
        remote_url = f"{webdav_url}{webdav_path.rstrip('/')}/{test_file_name}"
        auth = (webdav_username, webdav_password) if webdav_username else None

        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                await self._ensure_remote_dir(client, webdav_url, webdav_path, webdav_username, webdav_password)

                put_resp = await client.put(remote_url, content=b"pt-accelerator-webdav-test", auth=auth)
                if put_resp.status_code not in (200, 201, 204):
                    if put_resp.status_code in (401, 403):
                        return {"success": False, "message": "WebDAV 认证失败或无写入权限"}
                    if put_resp.status_code == 404:
                        return {"success": False, "message": "WebDAV 路径不存在或不可写"}
                    return {"success": False, "message": f"WebDAV 测试失败: HTTP {put_resp.status_code}"}

                delete_resp = await client.delete(remote_url, auth=auth)
                if delete_resp.status_code not in (200, 204, 404):
                    logger.warning(f"WebDAV 测试临时文件删除返回异常状态: {delete_resp.status_code}, url={remote_url}")

                return {"success": True, "message": "WebDAV 连接测试成功"}
        except httpx.TimeoutException:
            return {"success": False, "message": "WebDAV 连接超时，请检查地址、网络或服务器响应速度"}
        except httpx.ConnectError:
            return {"success": False, "message": "WebDAV 连接失败，请检查地址或网络连通性"}
        except Exception as e:
            logger.error(f"WebDAV 连接测试失败: {e}")
            return {"success": False, "message": f"WebDAV 测试失败: {str(e)}"}

    async def upload_to_webdav(self, backup_id: str) -> dict:
        """
        上传备份到 WebDAV

        Returns:
            {"success": bool, "message": str}
        """
        cfg = self._get_config()
        if not cfg.get("webdav_enabled"):
            return {"success": False, "message": "WebDAV 未启用"}

        webdav_url = cfg.get("webdav_url", "")
        webdav_user = cfg.get("webdav_username", "")
        webdav_pass = decrypt_secret(cfg.get("webdav_password", ""))  # 解密
        webdav_path = cfg.get("webdav_path", "/backups")

        if not webdav_url:
            return {"success": False, "message": "WebDAV URL 未配置"}

        backup = self._find_local_backup(backup_id)
        if not backup:
            return {"success": False, "message": f"本地备份不存在: {backup_id}"}

        local_path = backup.get("file_path", "")
        if not os.path.exists(local_path):
            return {"success": False, "message": f"备份文件不存在: {local_path}"}

        try:
            with open(local_path, "rb") as f:
                content = f.read()

            async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
                remote_url = self._build_remote_file_url(webdav_url, webdav_path, backup["file"])

                await self._ensure_remote_dir(client, webdav_url, webdav_path, webdav_user, webdav_pass)

                if webdav_user:
                    await client.delete(remote_url, auth=(webdav_user, webdav_pass))
                    resp = await client.put(remote_url, content=content, auth=(webdav_user, webdav_pass))
                else:
                    await client.delete(remote_url)
                    resp = await client.put(remote_url, content=content)

                if resp.status_code in (200, 201, 204):
                    logger.info(f"备份已上传到 WebDAV: {remote_url}")
                    return {"success": True, "message": "备份已上传到 WebDAV"}
                return {"success": False, "message": f"上传失败: HTTP {resp.status_code}"}
        except Exception as e:
            logger.error(f"WebDAV 上传失败: {e}")
            return {"success": False, "message": f"上传失败: {str(e)}"}

    async def _ensure_remote_dir(self, client: httpx.AsyncClient, webdav_url: str, webdav_path: str, webdav_user: str, webdav_pass: str):
        """递归确保远程目录存在，逐级创建（WebDAV MKCOL）。"""
        base = webdav_url.rstrip("/")
        path_parts = webdav_path.strip("/").split("/")
        current_path = ""
        for part in path_parts:
            if not part:
                continue
            current_path += "/" + part
            dir_url = base + current_path
            kwargs = {"auth": (webdav_user, webdav_pass)} if webdav_user else {}
            resp = await client.request("MKCOL", dir_url, **kwargs)
            if resp.status_code not in (201, 405):
                logger.debug(f"创建远程目录 {dir_url} 返回: {resp.status_code}")

    async def _download_remote_backup(self, backup: dict) -> str:
        cfg = self._get_config()
        webdav_url = cfg.get("webdav_url", "")
        webdav_user = cfg.get("webdav_username", "")
        webdav_pass = decrypt_secret(cfg.get("webdav_password", ""))  # 解密
        webdav_path = cfg.get("webdav_path", "/backups")

        if not webdav_url:
            raise ValueError("WebDAV URL 未配置")

        remote_url = self._build_remote_file_url(webdav_url, webdav_path, backup["file"])
        temp_dir = Path(self._backup_dir) / ".remote_restore"
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / backup["file"]

        auth = (webdav_user, webdav_pass) if webdav_user else None
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            resp = await client.get(remote_url, auth=auth)
            if resp.status_code == 404:
                raise ValueError(f"远程备份文件不存在: {backup['file']}")
            if resp.status_code in (401, 403):
                raise ValueError("远程备份下载失败：认证失败或无权限")
            if resp.status_code != 200:
                raise ValueError(f"远程备份下载失败: HTTP {resp.status_code}")
            temp_path.write_bytes(resp.content)

        return str(temp_path)

    @staticmethod
    def _is_safe_zip_member(member_name: str, extract_dir: str) -> bool:
        """
        校验 ZIP 成员路径是否安全（防御 Zip Slip 路径遍历攻击）。

        规则：
          1. 拒绝空文件名
          2. 拒绝包含 '..' 的路径组件
          3. 解析后的绝对路径必须以 extract_dir 为前缀
        """
        if not member_name:
            return False

        # 规范化路径，转为绝对路径
        safe_base = os.path.realpath(extract_dir)
        target = os.path.realpath(os.path.join(extract_dir, member_name))
        return target.startswith(safe_base + os.sep) or target == safe_base

    def _restore_zip(self, zip_path: str) -> dict:
        extract_dir = "config/restore_temp"
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zf:
            # 安全解压：逐成员校验路径，拒绝 Zip Slip 攻击
            for member in zf.infolist():
                if not self._is_safe_zip_member(member.filename, extract_dir):
                    logger.warning(f"备份恢复：跳过不安全的 ZIP 成员路径：{member.filename!r}")
                    continue
                zf.extract(member, extract_dir)

        for root, _, files in os.walk(extract_dir):
            for fname in files:
                src = os.path.join(root, fname)
                dst = os.path.join("config", fname)
                shutil.copy2(src, dst)

        shutil.rmtree(extract_dir)
        return {"success": True, "message": "备份已恢复，请重启应用"}

    async def restore_backup(self, backup_id: str) -> dict:
        """从本地或远程备份恢复。"""
        backup = self._find_backup(backup_id)
        if not backup:
            return {"success": False, "message": f"备份不存在: {backup_id}"}

        temp_remote_path = ""
        try:
            if backup.get("source") == "remote":
                temp_remote_path = await self._download_remote_backup(backup)
                result = self._restore_zip(temp_remote_path)
            else:
                local_path = backup.get("file_path", "")
                if not os.path.exists(local_path):
                    return {"success": False, "message": f"备份文件不存在: {local_path}"}
                result = self._restore_zip(local_path)

            logger.info(f"备份已恢复: {backup_id}")
            return result
        except Exception as e:
            logger.error(f"恢复备份失败: {e}")
            return {"success": False, "message": f"恢复失败: {str(e)}"}
        finally:
            if temp_remote_path and os.path.exists(temp_remote_path):
                try:
                    os.remove(temp_remote_path)
                except OSError:
                    pass

    async def delete_backup(self, backup_id: str) -> bool:
        """删除本地或远程备份。"""
        backup = self._find_backup(backup_id)
        if not backup:
            return False

        if backup.get("source") == "remote":
            cfg = self._get_config()
            webdav_url = (cfg.get("webdav_url") or "").strip().rstrip("/")
            webdav_user = cfg.get("webdav_username", "")
            webdav_pass = decrypt_secret(cfg.get("webdav_password", ""))  # 修复：解密后再使用
            webdav_path = (cfg.get("webdav_path") or "/backups").strip() or "/backups"
            file_name = backup.get("file", "")

            if not webdav_url or not file_name:
                return False

            remote_url = self._build_remote_file_url(webdav_url, webdav_path, file_name)
            auth = (webdav_user, webdav_pass) if webdav_user else None

            try:
                async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
                    response = await client.delete(remote_url, auth=auth)
            except Exception as e:
                logger.warning(f"删除远程备份失败: {e}")
                return False

            if response.status_code not in (200, 204):
                logger.warning(f"删除远程备份失败: HTTP {response.status_code}, url={remote_url}")
                return False
        else:
            local_path = backup.get("file_path", "")
            if local_path and os.path.exists(local_path):
                os.remove(local_path)
            else:
                return False

        logger.info(f"备份已删除: {backup_id}")
        return True


    def _collect_files(self) -> list[str]:
        """收集待备份文件"""
        files = []
        for f in DEFAULT_BACKUP_FILES:
            if os.path.exists(f):
                files.append(f)
        return files

    def _package_files(self, files: list[str]) -> str:
        """打包备份文件"""
        os.makedirs(self._backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_path = os.path.join(self._backup_dir, f"backup_{timestamp}.zip")

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                if os.path.exists(f):
                    zf.write(f, os.path.basename(f))

        logger.info(f"备份包已创建: {zip_path}")
        return zip_path

    def _cleanup_old_backups(self, keep_count: int):
        """清理旧本地备份，只保留最近 keep_count 个。"""
        backups = self._list_local_backups()
        if len(backups) <= keep_count:
            return

        for backup in backups[keep_count:]:
            local_path = backup.get("file_path", "")
            if local_path and os.path.exists(local_path):
                try:
                    os.remove(local_path)
                    logger.debug(f"已删除旧备份: {local_path}")
                except Exception as e:
                    logger.warning(f"删除旧备份失败: {e}")


# 全局单例
backup_service = BackupService()

