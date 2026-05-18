"""
CFST 调用、结果解析、IP 聚合

调用链路：
    routes/cfst.py → CfstService.run() → CFST 二进制 → 解析 CSV
                     ↓
              保存到 cache/ 供 Hosts Pipeline 使用

注意：
    运行阶段不再重复执行二进制安装/版本识别。
    CFST 的完整检测与安装流程只在应用启动阶段处理，运行时仅校验二进制是否存在。
"""

import csv
import os
import shlex
import subprocess
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


from app.config import config
from app.utils.cfst_installer import CfstInstaller
from app.utils.logger import get_logger

logger = get_logger(__name__)
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]



class CfstService:

    """CFST 测速服务（线程安全）"""

    def __init__(self):
        self._installer = CfstInstaller()
        self._running = False
        self._results: list[dict] = []
        self._task_id: Optional[str] = None
        self._started_at: Optional[datetime] = None
        self._progress = 0
        self._status_message = "空闲"
        self._lock = threading.Lock()

    @property
    def running(self) -> bool:
        return self._running

    @property
    def task_id(self) -> Optional[str]:
        return self._task_id

    @property
    def started_at(self) -> Optional[datetime]:
        return self._started_at

    @property
    def csv_results_file(self) -> Path:
        return self._get_default_result_file(self.get_binary())


    def get_binary(self) -> Path:
        """获取已在启动阶段确认存在的 CFST 二进制路径。"""
        binary_path = self._installer.get_binary_path()
        if not binary_path:
            raise RuntimeError("CFST 二进制路径为空")

        path = Path(binary_path).resolve()
        if not path.exists():
            raise RuntimeError(
                f"未找到 CFST 二进制文件：{binary_path}，请重启服务以触发启动阶段的自动检测/安装"
            )


        return path

    @staticmethod
    def _decode_output(data: bytes | None) -> str:
        """按常见编码容错解码子进程输出，避免 Windows 下编码导致异常。"""
        if not data:
            return ""

        for encoding in ("utf-8", "gb18030", "gbk"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue

        return data.decode("utf-8", errors="ignore")

    @staticmethod
    def _normalize_bool(value: bool) -> bool:
        return bool(value)

    def get_runtime_config(self) -> dict:
        """读取当前 CFST 官方参数配置。"""
        return {
            "threads": config.get("cfst.threads", default=200),
            "ping_times": config.get("cfst.ping_times", default=4),
            "download_count": config.get("cfst.download_count", default=20),
            "download_time": config.get("cfst.download_time", default=10),
            "timeout_seconds": config.get("cfst.timeout_seconds", default=300),
            "tcp_port": config.get("cfst.tcp_port", default=443),
            "url": config.get("cfst.url", default="") or "",
            "httping": self._normalize_bool(config.get("cfst.httping", default=False)),
            "httping_code": config.get("cfst.httping_code", default=""),
            "cfcolo": config.get("cfst.cfcolo", default=""),
            "min_delay": config.get("cfst.min_delay", default=0),
            "max_delay": config.get("cfst.max_delay", default=200),
            "max_loss_rate": config.get("cfst.max_loss_rate", default=1.0),
            "min_speed": config.get("cfst.min_speed", default=0.0),
            "show_count": config.get("cfst.show_count", default=10),
            "test_all": self._normalize_bool(config.get("cfst.test_all", default=False)),
            "disable_download": self._normalize_bool(config.get("cfst.disable_download", default=False)),
            "debug": self._normalize_bool(config.get("cfst.debug", default=False)),
            "additional_args": config.get("cfst.additional_args", default="") or "",
        }


    @staticmethod
    def _get_default_ip_file(binary_path: Path) -> Path:
        """获取与 CFST 二进制同目录的默认 IP 段文件。"""
        return (binary_path.parent / "ip.txt").resolve()

    @staticmethod
    def _get_default_result_file(binary_path: Path) -> Path:
        """获取与 CFST 二进制同目录的默认结果文件。"""
        return (binary_path.parent / "result.csv").resolve()


    @staticmethod
    def _to_log_path(path: Path) -> str:
        """日志中尽量显示相对工作区路径，读起来更短。"""
        try:
            return str(path.resolve().relative_to(WORKSPACE_ROOT)).replace("/", "\\")
        except ValueError:
            return str(path.resolve())

    @classmethod
    def _command_for_log(cls, cmd: list[str]) -> str:
        """日志里把工作区内绝对路径收口成相对路径，实际执行命令不受影响。"""
        normalized: list[str] = []
        for arg in cmd:
            try:
                path = Path(arg)
                if path.is_absolute():
                    normalized.append(cls._to_log_path(path))
                else:
                    normalized.append(arg)
            except (OSError, ValueError):
                normalized.append(arg)
        return " ".join(normalized)

    @staticmethod
    def _build_command(binary_path: Path, runtime_config: dict) -> list[str]:
        cmd = [str(binary_path)]

        cli_defaults = {

            "threads": 200,
            "ping_times": 4,
            "download_count": 20,
            "download_time": 10,
            "tcp_port": 443,
            "min_delay": 0,
            "max_delay": 200,
            "max_loss_rate": 1.0,
            "min_speed": 0.0,
            "show_count": 10,
        }
        value_flags = [
            ("threads", "-n"),
            ("ping_times", "-t"),
            ("download_count", "-dn"),
            ("download_time", "-dt"),
            ("tcp_port", "-tp"),
            ("min_delay", "-tll"),
            ("max_delay", "-tl"),
            ("max_loss_rate", "-tlr"),
            ("min_speed", "-sl"),
            ("show_count", "-p"),
        ]
        always_include_flags = {"download_count", "max_delay"}

        for config_key, flag in value_flags:
            value = runtime_config[config_key]
            if config_key in always_include_flags or value != cli_defaults[config_key]:
                cmd.extend([flag, str(value)])

        default_url = "https://cf.xiu2.xyz/url"
        if runtime_config["url"] and str(runtime_config["url"]).strip() != default_url:
            cmd.extend(["-url", str(runtime_config["url"])])

        if runtime_config["httping"]:
            cmd.append("-httping")
        if runtime_config["httping_code"]:
            cmd.extend(["-httping-code", str(runtime_config["httping_code"])])
        if runtime_config["cfcolo"]:
            cmd.extend(["-cfcolo", str(runtime_config["cfcolo"] )])
        if runtime_config["test_all"]:
            cmd.append("-allip")
        if runtime_config["disable_download"]:
            cmd.append("-dd")
        if runtime_config["debug"]:
            cmd.append("-debug")
        if runtime_config["additional_args"]:
            cmd.extend(shlex.split(str(runtime_config["additional_args"]), posix=False))

        return cmd


    @staticmethod
    def _row_value(row: dict, *keys: str) -> str:
        for key in keys:
            if key in row and row[key] not in (None, ""):
                return str(row[key]).strip()
        return ""

    @staticmethod
    def _to_int(value: str) -> Optional[int]:
        if value == "":
            return None
        try:
            return int(float(value))
        except ValueError:
            return None

    @staticmethod
    def _to_float(value: str) -> Optional[float]:
        if value == "":
            return None
        try:
            return float(value)
        except ValueError:
            return None

    def parse_result_csv(self, csv_path: Path) -> list[dict]:
        """解析 CFST 输出 CSV。"""
        if not csv_path.exists():
            return []

        try:
            with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                parsed_results: list[dict] = []
                for row in reader:
                    parsed_results.append(
                        {
                            "ip": self._row_value(row, "IP 地址", "IP", "ip"),
                            "sent": self._to_int(self._row_value(row, "已发送", "发送", "send", "sent")),
                            "received": self._to_int(self._row_value(row, "已接收", "接收", "recv", "received")),
                            "loss_rate": self._to_float(
                                self._row_value(row, "丢包率(%)", "丢包率", "loss", "loss_rate")
                            ),
                            "avg_latency": self._to_float(
                                self._row_value(row, "平均延迟(ms)", "平均延迟", "latency", "delay")
                            ),
                            "download_speed": self._to_float(
                                self._row_value(row, "下载速度(MB/s)", "下载速度", "speed", "download_speed")
                            ),
                            "location": self._row_value(row, "地区码(Colo)", "地区码", "colo", "location"),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
        except FileNotFoundError:
            return []

        return parsed_results

    def _get_file_snapshot(self, csv_path: Path) -> tuple[int, int] | None:
        """获取结果文件当前快照（大小 + 修改时间纳秒）。"""
        if not csv_path.exists():
            return None
        stat = csv_path.stat()
        return stat.st_size, stat.st_mtime_ns

    def _try_parse_existing_results(self, csv_path: Path) -> list[dict]:
        """尝试解析当前结果文件，解析失败时返回空列表。"""
        try:
            return self.parse_result_csv(csv_path)
        except Exception as e:
            logger.debug(f"CFST 结果文件暂不可解析，等待继续写入：{e}")
            return []

    def _terminate_process(self, process: subprocess.Popen, reason: str):
        """结束仍在运行的 CFST 子进程。"""
        if process.poll() is not None:
            return

        logger.info(f"准备结束 CFST 子进程：{reason}")
        try:
            process.terminate()
            process.wait(timeout=5)
            logger.info("CFST 子进程已正常结束")
        except subprocess.TimeoutExpired:
            logger.warning("CFST 子进程未在 5 秒内退出，改为强制结束")
            process.kill()
            process.wait(timeout=5)
        except Exception as e:
            logger.warning(f"结束 CFST 子进程时出现异常：{e}")

    def _wait_for_completion_or_result_file(
        self,
        process: subprocess.Popen,
        csv_path: Path,
        timeout_seconds: int,
    ) -> tuple[bool, list[dict]]:
        """等待进程结束，或在 Windows 下检测结果文件稳定落盘后提前接管。"""
        deadline = time.monotonic() + timeout_seconds
        last_snapshot: tuple[int, int] | None = None
        stable_rounds = 0

        while time.monotonic() < deadline:
            if process.poll() is not None:
                # 进程已退出（正常完成或异常），尝试立即读取结果文件
                parsed = self._try_parse_existing_results(csv_path)
                if parsed:
                    return True, parsed
                return False, []

            if os.name == "nt":
                snapshot = self._get_file_snapshot(csv_path)
                if snapshot and snapshot[0] > 0:
                    if snapshot == last_snapshot:
                        stable_rounds += 1
                    else:
                        stable_rounds = 0
                        last_snapshot = snapshot

                    if stable_rounds >= 2:
                        parsed_results = self._try_parse_existing_results(csv_path)
                        if parsed_results:
                            return True, parsed_results
                else:
                    last_snapshot = None
                    stable_rounds = 0

            time.sleep(1)

        return False, []

    @classmethod
    def _clear_old_result_file(cls, csv_path: Path):
        """删除旧结果文件；按用户要求只做直接删除，不再回退改名。"""
        if not csv_path.exists():
            logger.debug(f"CFST 启动前未发现旧结果文件：{cls._to_log_path(csv_path)}")
            return

        for attempt in range(1, 4):
            try:
                csv_path.unlink()
                logger.info(f"已删除旧 CFST 结果文件：{cls._to_log_path(csv_path)}")
                return
            except PermissionError as e:
                if attempt < 3:
                    logger.warning(
                        f"旧 CFST 结果文件删除时被占用，准备第 {attempt + 1} 次重试：{cls._to_log_path(csv_path)}"
                    )
                    time.sleep(0.5)
                    continue
                logger.warning(f"旧 CFST 结果文件仍被占用，未执行改名回退：{type(e).__name__}: {e}")
                return
            except Exception as e:
                logger.warning(f"删除旧 CFST 结果文件失败：{type(e).__name__}: {e}")
                return



    def run(self) -> str:
        """启动后台 CFST 测速任务，并返回任务 ID。"""
        with self._lock:
            if self._running:
                raise RuntimeError(f"CFST 正在运行中（task_id={self._task_id}）")

            task_id = uuid.uuid4().hex[:8]
            self._running = True
            self._task_id = task_id
            self._started_at = datetime.now()
            self._progress = 0
            self._status_message = "测速进行中"
            self._results = []

        self.csv_results_file.parent.mkdir(parents=True, exist_ok=True)
        worker = threading.Thread(target=self._run_sync, name=f"cfst-{task_id}", daemon=True)


        worker.start()
        logger.info(f"CFST 后台任务已启动：{task_id}")
        return task_id

    def _run_sync(self):
        process: subprocess.Popen | None = None
        try:
            binary_path = self.get_binary()
            runtime_config = self.get_runtime_config()
            result_file = self._get_default_result_file(binary_path)
            logger.info(f"CFST 二进制路径：{self._to_log_path(binary_path)}")

            self._clear_old_result_file(result_file)

            cmd = self._build_command(binary_path, runtime_config)
            logger.info(f"CFST 输入文件：{self._to_log_path(self._get_default_ip_file(binary_path))}")
            logger.info(f"CFST 结果文件：{self._to_log_path(result_file)}")
            logger.info(f"开始执行 CFST：{self._command_for_log(cmd)}")
            timeout_seconds = max(int(runtime_config.get("timeout_seconds", 300) or 300), 30)
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False,
                cwd=str(binary_path.parent),
            )


            # 启动后台线程实时转发 CFST 输出到日志
            # 过滤掉刷屏内容：光标进度条、测速结果行、完成提示、退出提示
            import re as _re

            _skip_pattern = _re.compile(
                r"[↘↙↖↗→←↑↓]|[▊▋▌▍▎▏]|[═\-_]{10,}|^\s*\[[\d\/\s]+\]\s*\["   # 光标进度条
                r"|^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s+\d+"               # 测速结果行（IP + 数字）
                r"|完整测速结果已写入|按下.*退出"                             # 完成/退出提示
            )

            def _stream_output(proc: subprocess.Popen):
                assert proc.stdout is not None
                for raw_line in proc.stdout:
                    line = raw_line.decode("utf-8", errors="replace").rstrip()
                    if line and not _skip_pattern.search(line):
                        logger.info(f"[cfst] {line}")

            import threading as _threading
            _output_thread = _threading.Thread(target=_stream_output, args=(process,), daemon=True)
            _output_thread.start()

            completed_from_result_file, parsed_results = self._wait_for_completion_or_result_file(
                process=process,
                csv_path=result_file,
                timeout_seconds=timeout_seconds,
            )

            if completed_from_result_file:
                logger.info("CFST 结果文件已稳定落盘，准备结束仍停留在交互退出阶段的子进程")
                self._terminate_process(process, reason="结果文件已稳定落盘")
                with self._lock:
                    self._results = parsed_results
                    self._status_message = f"测速完成，共 {len(parsed_results)} 条结果"
                logger.info(f"CFST 执行完成（按结果文件接管），共解析到 {len(parsed_results)} 条结果")
                return

            if process.poll() is None:
                raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout_seconds)

            # stdout 已由 _stream_output 线程消耗完毕，等待线程结束即可
            _output_thread.join(timeout=5)

            if process.returncode != 0:
                raise RuntimeError(f"CFST 退出码为 {process.returncode}")

            parsed_results = self.parse_result_csv(result_file)

            with self._lock:
                self._results = parsed_results
                self._status_message = f"测速完成，共 {len(parsed_results)} 条结果"

            logger.info(f"CFST 执行完成，共解析到 {len(parsed_results)} 条结果")

        except subprocess.TimeoutExpired:
            logger.error("CFST 执行超时")
            if process is not None:
                self._terminate_process(process, reason="执行超时")
            if not self._load_existing_results_after_timeout():
                with self._lock:
                    self._results = [{
                        "ip": "",
                        "sent": None,
                        "received": None,
                        "loss_rate": None,
                        "avg_latency": None,
                        "download_speed": None,
                        "location": "",
                        "timestamp": datetime.now().isoformat(),
                        "error": "测速超时",
                    }]
                    self._status_message = "测速超时"
        except Exception as e:
            logger.error(f"CFST 执行异常：{e}", exc_info=True)
            if process is not None:
                self._terminate_process(process, reason="执行异常")
            self._set_error(str(e))
        finally:
            with self._lock:
                self._running = False
                self._progress = 100

    def _load_existing_results_after_timeout(self) -> bool:
        """超时时如果结果文件已经落盘，则优先接管已有结果。"""
        result_file = self.csv_results_file
        if not result_file.exists():
            return False

        parsed_results = self.parse_result_csv(result_file)
        if not parsed_results:
            return False

        with self._lock:
            self._results = parsed_results
            self._status_message = f"测速超时，但已接管 {len(parsed_results)} 条结果"

        logger.warning(f"CFST 执行超时，但已从 CSV 接管 {len(parsed_results)} 条结果")
        return True

    def _set_error(self, message: str):
        with self._lock:
            self._running = False
            self._progress = 100
            self._status_message = message
            self._results = [{
                "ip": "",
                "sent": None,
                "received": None,
                "loss_rate": None,
                "avg_latency": None,
                "download_speed": None,
                "location": "",
                "timestamp": datetime.now().isoformat(),
                "error": message,
            }]

    def get_results(self) -> list[dict]:
        with self._lock:
            if self._results:
                return self._results.copy()

        return self.parse_result_csv(self.csv_results_file)


    def get_best_result(self) -> Optional[dict]:
        results = self.get_results()
        if not results or results[0].get("error"):
            return None
        return results[0]

    def get_cached_results(self) -> dict[str, str]:
        """兼容旧调用方：返回 tracker URL -> 当前最优 IP 的映射。"""
        best_result = self.get_best_result()
        best_ip = best_result.get("ip") if best_result else None
        if not best_ip:
            return {}

        from app.services.tracker_service import tracker_service

        return {
            tracker.get("url", ""): best_ip
            for tracker in tracker_service.list_enabled_cloudflare()
            if tracker.get("url")
        }

    def get_status(self) -> dict:
        result_file = self.csv_results_file
        with self._lock:
            running = self._running
            result_count = len(self._results) if self._results else 0
            if not running and result_count == 0:
                result_count = len(self.parse_result_csv(result_file))
            return {
                "running": running,
                "task_id": self._task_id,
                "progress": self._progress,
                "started_at": self._started_at,
                "result_count": result_count,
                "message": self._status_message,
            }


cfst_service = CfstService()
