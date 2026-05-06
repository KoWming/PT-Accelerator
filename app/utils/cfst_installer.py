"""
CFST (Cloudflare Speed Test) 二进制安装器

功能：
  - GitHub API 获取最新版本
  - 多平台支持（Windows/Mac/Linux）
  - 架构检测（amd64/arm64）
  - 自动下载/解压
  - 版本比较（只下载新版本）
  - 旧版本兼容（CloudflareST -> cfst）
  - 代理支持
"""
import os
import platform
import re
import stat
import subprocess
import zipfile
import tarfile
import shutil
import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)

# 安装目录
BIN_DIR = "CFST"

# GitHub 发布信息
RELEASE_API = "https://api.github.com/repos/XIU2/CloudflareSpeedTest/releases/latest"
RELEASE_PREFIX = "https://github.com/XIU2/CloudflareSpeedTest/releases/download"
FALLBACK_VERSION = "v2.3.4"
VERSION_FALLBACK = "local"
VERSION_PATTERN = re.compile(r"CloudflareSpeedTest\s+(v\d+\.\d+\.\d+)", re.IGNORECASE)



# 二进制名称映射（v2.x 版本统一使用 cfst 前缀）
BINARY_NAME = "cfst"          # 当前版本名称
BINARY_NAME_LEGACY = "CloudflareST"  # 旧版本名称（兼容）

# 平台到下载文件名的映射（v2.x 版本后改为 cfst 前缀）
PLATFORM_FILES = {
    ("Windows", "AMD64"): ("cfst_windows_amd64.zip", "zip"),
    ("Windows", "x86_64"): ("cfst_windows_amd64.zip", "zip"),
    ("Darwin", "x86_64"): ("cfst_darwin_amd64.zip", "zip"),
    ("Darwin", "arm64"): ("cfst_darwin_arm64.zip", "zip"),
    ("Linux", "x86_64"): ("cfst_linux_amd64.tar.gz", "tar.gz"),
    ("Linux", "amd64"): ("cfst_linux_amd64.tar.gz", "tar.gz"),
    ("Linux", "aarch64"): ("cfst_linux_arm64.tar.gz", "tar.gz"),
    ("Linux", "arm64"): ("cfst_linux_arm64.tar.gz", "tar.gz"),
}


class CfstInstaller:
    """CFST 二进制安装器"""

    def __init__(self, base_dir: str = BIN_DIR):
        self._base_dir = base_dir
        self._system = platform.system()
        self._machine = self._normalize_arch(platform.machine())

    def _normalize_arch(self, arch: str) -> str:
        """标准化架构名称"""
        arch_lower = arch.lower()
        if arch_lower in ("amd64", "x86_64"):
            return "AMD64"
        elif arch_lower in ("aarch64", "arm64", "armv8"):
            return "ARM64"
        elif arch_lower in ("armv7l", "armv7"):
            return "ARM"
        return arch

    def _get_platform_key(self) -> tuple:
        """获取平台键"""
        return (self._system, self._machine)

    def _get_download_file(self) -> tuple:
        """获取下载文件名和格式"""
        key = self._get_platform_key()
        if key in PLATFORM_FILES:
            return PLATFORM_FILES[key]
        # 默认使用 Linux amd64
        return ("cfst_linux_amd64.tar.gz", "tar.gz")

    def get_binary_name(self) -> str:
        """获取当前平台对应的二进制文件名"""
        # v2.x 版本统一使用 cfst 前缀
        if self._system == "Windows":
            return "cfst.exe"
        return "cfst"

    def get_binary_path(self) -> str:
        """获取二进制文件路径"""
        binary_name = self.get_binary_name()
        new_path = os.path.join(self._base_dir, binary_name)
        if os.path.exists(new_path):
            return new_path

        # 兼容旧路径和新路径
        legacy_names = [
            "CloudflareST.exe", "CloudflareST",
            "cfst.exe", "cfst",
        ]
        for name in legacy_names:
            path = os.path.join(self._base_dir, name)
            if os.path.exists(path):
                logger.info(f"找到 CFST 二进制文件：{path}")
                return path

        # 查找 legacy 目录
        legacy_paths = [
            os.path.join("bin", binary_name),
            os.path.join("cfst", binary_name),
        ]
        for p in legacy_paths:
            if os.path.exists(p):
                logger.info(f"找到 CFST 二进制文件（旧路径）：{p}")
                return p

        return new_path

    def get_expected_install_path(self) -> str:
        """获取期望安装路径"""
        return os.path.join(self._base_dir, self.get_binary_name())

    def get_version(self) -> str:
        """获取已安装的版本（从配置读取）"""
        from app.config import config
        return config.get("cfst.version", "")

    def set_version(self, version: str):
        """保存版本到配置"""
        from app.config import config
        config.set("cfst.version", version)
        config.save()

    def _get_latest_version(self) -> str:
        """获取 GitHub 最新版本"""
        try:
            # 尝试使用代理
            proxy_host = os.environ.get("PROXY_HOST", "")
            if proxy_host:
                url = f"{proxy_host}/{RELEASE_API}"
            else:
                url = RELEASE_API

            with httpx.Client(timeout=30) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    version = data.get("tag_name", "")
                    logger.info(f"最新 CFST 版本：{version}")
                    return version
                else:
                    logger.warning(f"获取最新版本失败：{resp.status_code}")
        except Exception as e:
            logger.warning(f"获取最新版本失败：{e}")

        return ""

    def get_download_url(self, version: str) -> str:
        """获取指定版本下载链接"""
        file_name, _ = self._get_download_file()
        return f"{RELEASE_PREFIX}/{version}/{file_name}"

    def get_manual_download_url(self) -> str:
        """获取手动下载链接"""
        version = self._get_latest_version() or FALLBACK_VERSION
        return self.get_download_url(version)

    def _download_file(self, url: str, dest_path: str) -> bool:
        """下载文件"""
        try:
            # 获取代理设置
            proxy = os.environ.get("PROXY_HOST", "") or None

            client_kwargs = {"timeout": 120, "follow_redirects": True}
            if proxy:
                client_kwargs["proxy"] = proxy

            with httpx.Client(**client_kwargs) as client:
                logger.info(f"正在下载 CFST：{url}")
                with client.stream("GET", url) as resp:
                    resp.raise_for_status()
                    total_size = int(resp.headers.get("content-length", 0))

                    os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)
                    with open(dest_path, "wb") as f:
                        downloaded = 0
                        for chunk in resp.iter_bytes(chunk_size=8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                if downloaded % (1024 * 1024) == 0:  # 每 MB 输出一次
                                    logger.debug(f"下载进度：{progress:.1f}%")

            logger.info(f"下载完成：{dest_path}")
            return True
        except Exception as e:
            logger.error(f"下载失败：{e}")
            if os.path.exists(dest_path):
                os.remove(dest_path)
            return False

    def _extract_file(self, archive_path: str, fmt: str) -> bool:
        """解压文件"""
        try:
            logger.info(f"正在解压：{archive_path}")

            if fmt == "zip":
                with zipfile.ZipFile(archive_path, "r") as zf:
                    zf.extractall(self._base_dir)
            elif fmt == "tar.gz":
                with tarfile.open(archive_path, "r:gz") as tf:
                    tf.extractall(self._base_dir)
            else:
                logger.error(f"不支持的压缩格式：{fmt}")
                return False

            # 删除压缩包
            os.remove(archive_path)
            logger.info("解压完成")
            return True
        except Exception as e:
            logger.error(f"解压失败：{e}")
            return False

    def _find_local_archive(self) -> tuple[str, str] | tuple[None, None]:
        """查找 CFST 目录中的本地安装包"""
        file_name, fmt = self._get_download_file()
        candidates = [
            os.path.join(self._base_dir, file_name),
            os.path.join(self._base_dir, f"CloudflareST_{file_name.split('_', 1)[1]}"),
        ]

        for path in candidates:
            if os.path.exists(path):
                logger.info(f"检测到本地 CFST 安装包：{path}")
                return path, fmt

        return None, None

    def _decode_output(self, data: bytes | None) -> str:
        """按常见编码容错解码子进程输出"""
        if not data:
            return ""

        for encoding in ("utf-8", "gb18030", "gbk"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue

        return data.decode("utf-8", errors="ignore")

    def _read_binary_version(self, binary_path: str) -> str:
        """通过帮助输出识别 CFST 版本"""
        commands = []
        if self._system == "Windows":
            commands.append([binary_path, "-h"])
        else:
            commands.extend([
                [binary_path, "-h"],
                [binary_path, "--help"],
            ])

        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=False,
                    timeout=15,
                )
                output = self._decode_output(result.stdout) + "\n" + self._decode_output(result.stderr)
                first_line = output.strip().splitlines()[0] if output.strip() else ""
                match = VERSION_PATTERN.search(first_line)
                if match:
                    version = match.group(1)
                    logger.info(f"已识别 CFST 版本：{version}")
                    return version
            except Exception as e:
                logger.warning(f"读取 CFST 版本失败：命令={' '.join(cmd)}，错误：{e}")

        logger.warning(f"CFST 已安装，但暂时无法识别版本，将使用兜底版本：{VERSION_FALLBACK}")
        return VERSION_FALLBACK


    def _record_binary_version(self, binary_path: str) -> str:
        """识别并保存二进制版本"""
        version = self._read_binary_version(binary_path)
        self.set_version(version)
        return version


    def _install_from_local_archive(self) -> bool:
        """优先从本地压缩包安装 CFST"""
        archive_path, fmt = self._find_local_archive()
        if not archive_path or not fmt:
            return False

        if not self._extract_file(archive_path, fmt):
            logger.error("本地 CFST 安装包解压失败")
            return False

        binary_path = self.get_binary_path()
        if not os.path.exists(binary_path):
            logger.error("本地安装包解压后未找到 CFST 二进制文件")
            return False

        self._set_executable(binary_path)
        installed_version = self._record_binary_version(binary_path)
        logger.info(f"已通过本地安装包完成 CFST 安装：{binary_path}（{installed_version}）")
        return True



    def _set_executable(self, binary_path: str):
        """设置可执行权限"""
        if self._system != "Windows":
            try:
                current = os.stat(binary_path).st_mode
                os.chmod(binary_path, current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                logger.debug(f"设置可执行权限：{binary_path}")
            except Exception as e:
                logger.warning(f"设置可执行权限失败：{e}")

    def check_update(self) -> tuple:
        """
        检查是否有更新

        Returns:
            (need_update: bool, latest_version: str)
        """
        current_version = self.get_version()
        latest_version = self._get_latest_version()

        if not latest_version:
            logger.warning("无法获取最新版本")
            return False, ""

        need_update = current_version != latest_version
        if need_update:
            logger.info(f"有可用更新：{current_version} -> {latest_version}")
        else:
            logger.info(f"CFST 已是最新版本：{current_version}")

        return need_update, latest_version

    def install_latest(self) -> bool:
        """下载安装最新版本 CFST"""
        latest_version = self._get_latest_version()
        if not latest_version:
            latest_version = FALLBACK_VERSION
            logger.warning(f"无法获取最新版本信息，改用默认版本：{latest_version}")

        file_name, fmt = self._get_download_file()
        download_url = self.get_download_url(latest_version)
        archive_path = os.path.join(self._base_dir, file_name)

        os.makedirs(self._base_dir, exist_ok=True)

        if not self._download_file(download_url, archive_path):
            manual_url = self.get_download_url(latest_version)
            logger.error("CFST 自动下载失败，请手动下载安装。")
            logger.error(f"手动下载链接：{manual_url}")
            logger.error(f"请将二进制文件放入目录：{os.path.abspath(self._base_dir)}")
            logger.error("放置完成后请重启服务，系统会重新检测并安装。")
            return False

        if not self._extract_file(archive_path, fmt):
            manual_url = self.get_download_url(latest_version)
            logger.error("CFST 自动安装失败，请手动下载安装。")
            logger.error(f"手动下载链接：{manual_url}")
            logger.error(f"请将二进制文件放入目录：{os.path.abspath(self._base_dir)}")
            logger.error("放置完成后请重启服务，系统会重新检测并安装。")
            return False

        binary_path = self.get_binary_path()
        if not os.path.exists(binary_path):
            logger.error("解压后未找到 CFST 二进制文件")
            logger.error(f"请手动下载安装：{self.get_download_url(latest_version)}")
            logger.error(f"目标目录：{os.path.abspath(self._base_dir)}")
            return False

        self._set_executable(binary_path)
        installed_version = self._record_binary_version(binary_path)
        logger.info(f"CFST 安装成功：{binary_path}（{installed_version}）")
        return True


    def ensure(self, force_reinstall: bool = False) -> bool:
        """
        确保 CFST 二进制存在

        Args:
            force_reinstall: 是否强制重新安装

        Returns:
            bool: 安装是否成功
        """
        binary_path = self.get_binary_path()
        binary_exists = os.path.exists(binary_path)

        if force_reinstall and binary_exists:
            logger.info("强制重装，删除现有 CFST 二进制文件")
            try:
                os.remove(binary_path)
                binary_exists = False
            except Exception as e:
                logger.error(f"删除现有二进制文件失败：{e}")
                return False

        if binary_exists:
            logger.info(f"CFST 二进制文件已存在：{binary_path}")
            self._record_binary_version(binary_path)
            return True

        if self._install_from_local_archive():
            return True

        logger.warning("未检测到可用 CFST 二进制文件或本地安装包，开始自动下载安装")
        return self.install_latest()

    def uninstall(self) -> bool:
        """卸载 CFST 二进制"""
        try:
            binary_path = self.get_binary_path()
            if os.path.exists(binary_path):
                os.remove(binary_path)
                logger.info(f"CFST 已卸载：{binary_path}")

            # 清理版本记录
            from app.config import config
            config.set("cfst.version", "")
            config.save()

            return True
        except Exception as e:
            logger.error(f"卸载失败：{e}")
            return False


