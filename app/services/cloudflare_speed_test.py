import logging
import os
import subprocess
import time
import shutil
import platform
from typing import Dict, Any

from app.services.hosts_manager import HostsManager

logger = logging.getLogger(__name__)

class CloudflareSpeedTestService:
    """CloudflareSpeedTest服务，用于测试优选Cloudflare IP"""
    
    def __init__(self, config: Dict[str, Any], hosts_manager: HostsManager):
        self.config = config
        self.hosts_manager = hosts_manager
        
        # 工作目录
        self.base_dir = os.getcwd()
        logger.info(f"当前工作目录: {self.base_dir}")
        
        # 查找CloudflareSpeedTest可执行文件
        self.cft_path = self._find_cloudflare_st()
        self.bin_dir = os.path.dirname(self.cft_path)
        
        # 结果和IP文件路径
        self.result_file = os.path.join(self.base_dir, "result.csv")
        self.result_v4_file = os.path.join(self.base_dir, "result_v4.csv")
        self.result_v6_file = os.path.join(self.base_dir, "result_v6.csv")
        self.ip_file = os.path.join(self.base_dir, "ip.txt")
        self.ipv6_file = os.path.join(self.base_dir, "ipv6.txt")
        
        # 记录当前状态
        self.running = False
        
        # 输出初始化信息
        logger.info(f"CloudflareSpeedTest可执行文件: {self.cft_path}")
        logger.info(f"CloudflareSpeedTest目录: {self.bin_dir}")
        logger.info(f"IP文件路径: {self.ip_file}")
        logger.info(f"IPv6文件路径: {self.ipv6_file}")
        logger.info(f"结果文件路径: {self.result_file}")
        
        # 确保IP文件存在
        self._ensure_ip_files()
        
    def _find_cloudflare_st(self) -> str:
        """查找CloudflareSpeedTest可执行文件，支持架构自适应"""
        # 获取架构目录
        arch_dir = self._get_arch_dir()
        machine = platform.machine().lower()
        logger.info(f"检测到架构: {machine}, 使用目录: {arch_dir}")
        
        # 可能的路径，按架构自适应
        possible_paths = [
            # 在当前目录查找
            os.path.join(self.base_dir, "cfst"),
            os.path.join(self.base_dir, arch_dir, "cfst"),
            
            # 在系统目录查找
            "/usr/local/bin/cfst",
            "/usr/bin/cfst",
            
            # 在Docker环境中的路径
            "/app/cfst",
            f"/app/{arch_dir}/cfst"
        ]
        
        # 输出所有可能的路径方便调试
        logger.info("正在查找CloudflareSpeedTest可执行文件...")
        for path in possible_paths:
            logger.info(f"检查路径: {path} - {'存在' if os.path.exists(path) else '不存在'}")
        
        # 查找可执行文件
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                logger.info(f"找到可执行的CloudflareSpeedTest: {path}")
                return path
                
        # 如果没有找到可执行文件，使用架构自适应的默认路径并发出警告
        default_path = f"./{arch_dir}/cfst"
        logger.warning(f"未找到CloudflareSpeedTest可执行文件，将使用默认路径 {default_path}")
        return default_path
        
    def update_config(self, config: Dict[str, Any]):
        """更新配置"""
        self.config = config

    # ─────────────────────────────────────────────
    # 核心：单次进程执行
    # ─────────────────────────────────────────────
    def _run_cfst_process(self, use_ipv6: bool, result_out: str, additional_args: str = "") -> Dict[str, Any]:
        """启动一个 CloudflareST 子进程并等待它完成，返回 {success, logs}"""
        tag = "[IPv6]" if use_ipv6 else "[IPv4]"
        ip_src = self.ipv6_file if use_ipv6 else self.ip_file

        if not os.path.exists(ip_src):
            msg = f"{tag} IP文件不存在: {ip_src}"
            logger.error(msg)
            return {"success": False, "logs": [msg]}

        cmd = [self.cft_path]
        cmd.extend(["-o", result_out])
        cmd.extend(["-f", ip_src])

        # 默认附加 "-dd" (关闭下载测速) 和 "-p 0" (不显示控制台结果列表) 
        # 以还原原版 Shell 脚本的高速执行体验。若用户自定义中已提供类似的参数，则不重复添加。
        args_str = additional_args if additional_args else ""
        if "-dd" not in args_str:
            cmd.append("-dd")
        if "-p" not in args_str:
            cmd.extend(["-p", "0"])

        if additional_args:
            for arg in additional_args.split():
                if arg.strip() and arg.strip() != "-ipv4":
                    cmd.append(arg.strip())

        logger.info(f"{tag} 执行命令: {' '.join(cmd)}")
        logs: list = []
        try:
            # 引入 5 分钟超时，防止由于没有有效 IPv6 路由导致的 TCP Connect 无限挂起
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.base_dir,
                timeout=300
            )
            
            # 由于 cfst 会使用 \r 刷新进度条，按行获取输出极其冗长且易死锁
            # 我们仅保留错误输出和关键结果，以保持日志整洁
            if process.stderr:
                logger.error(f"{tag} 测速输出警告/错误: {process.stderr.strip()}")
                logs.append(f"错误: {process.stderr.strip()}")
                
            if process.returncode == 0:
                logger.info(f"{tag} 测速正常完成 (返回码: 0)")
                return {"success": True, "logs": logs}
            else:
                logger.warning(f"{tag} 测速退出异常 (返回码: {process.returncode})")
                return {"success": False, "logs": logs}
                
        except subprocess.TimeoutExpired:
            logger.error(f"{tag} 进程执行超时 (超过 300 秒)，已强制终止。可能原因：网络无路由导致 TCP Connect 挂起，或下载测速节点过多。")
            logs.append("错误: 进程执行超时已被系统终止")
            return {"success": False, "logs": logs}
        except Exception as exc:
            logger.error(f"{tag} 进程异常: {exc}")
            return {"success": False, "logs": [f"错误: {exc}"]}

    # ─────────────────────────────────────────────
    # 结果解析
    # ─────────────────────────────────────────────
    def _parse_best_from_csv(self, csv_path: str) -> tuple:
        """从 result CSV 中解析出最优 IP 和对应下载速度，返回 (ip, speed)；找不到返回 (None, 0)"""
        if not os.path.exists(csv_path):
            return None, 0
        try:
            with open(csv_path, "r") as f:
                lines = f.readlines()
            if len(lines) <= 1:
                return None, 0
            headers = lines[0].strip().split(",")
            ip_idx = headers.index("IP")
            spd_idx = headers.index("下载速度 (MB/s)")
            best_ip, best_speed = None, 0.0
            for row in lines[1:]:
                cols = row.strip().split(",")
                if len(cols) > max(ip_idx, spd_idx):
                    try:
                        speed = float(cols[spd_idx])
                        if speed > best_speed:
                            best_speed = speed
                            best_ip = cols[ip_idx]
                    except ValueError:
                        continue
            return best_ip, best_speed
        except Exception as e:
            logger.error(f"解析结果文件出错 {csv_path}: {e}")
            return None, 0

    def _apply_best_ip(self, best_ip: str, best_speed: float):
        """将最优 IP 写入所有启用的 Tracker"""
        logger.info(f"[优选结果] 最优IP: {best_ip}，速度: {best_speed:.2f} MB/s")
        for tracker in self.config.get("trackers", []):
            if tracker.get("enable", False):
                domain = tracker.get("domain")
                if domain:
                    logger.info(f"为 {domain} 设置新IP: {best_ip}")
                    self.hosts_manager.add_cloudflare_ip(domain, best_ip)

    def _apply_dual_stack_ips(self, ipv4: str, ipv6: str):
        """双栈写入：将 IPv4 + IPv6 同时写入所有启用的 Tracker"""
        logger.info(f"[双栈写入] IPv4={ipv4}  IPv6={ipv6}")
        # 先批量设置配置中的 ip/ip6 字段
        self.hosts_manager._update_all_trackers_dual_stack(ipv4, ipv6)
        # _update_all_trackers_dual_stack 内部已调用 update_hosts()，无需重复调用
    
    def _get_arch_dir(self) -> str:
        """获取当前架构对应的目录名"""
        machine = platform.machine().lower()
        if machine in ("aarch64", "arm64"):
            return "cfst_linux_arm64"
        else:
            return "cfst_linux_amd64"
    
    def _ensure_ip_files(self):
        """确保IP文件存在"""
        logger.info(f"确保IP文件存在: {self.ip_file}")
        
        # 检查当前目录下是否已存在ip.txt
        if os.path.exists(self.ip_file):
            logger.info(f"IP文件已存在: {self.ip_file}")
            self._verify_ip_file(self.ip_file)
            return
        
        # 未找到ip.txt，尝试在可执行文件同目录下查找
        bin_dir_ip_file = os.path.join(self.bin_dir, "ip.txt")
        if os.path.exists(bin_dir_ip_file):
            logger.info(f"在可执行文件目录下找到IP文件: {bin_dir_ip_file}")
            try:
                # 复制到当前目录
                shutil.copy(bin_dir_ip_file, self.ip_file)
                logger.info(f"已复制IP文件: {bin_dir_ip_file} -> {self.ip_file}")
                self._verify_ip_file(self.ip_file)
                return
            except Exception as e:
                logger.error(f"复制IP文件失败: {str(e)}")
        
        # 在其他可能位置查找，支持架构自适应
        logger.info("在其他位置查找IP文件...")
        # 获取架构目录
        arch_dir = self._get_arch_dir()
        
        possible_paths = [
            os.path.join(self.base_dir, arch_dir, "ip.txt"),
            "/usr/local/bin/ip.txt",
            "/usr/local/share/CloudflareST/ip.txt",
            "/app/ip.txt"
        ]
        
        for path in possible_paths:
            logger.info(f"检查路径: {path} - {'存在' if os.path.exists(path) else '不存在'}")
            if os.path.exists(path):
                try:
                    shutil.copy(path, self.ip_file)
                    logger.info(f"已复制IP文件: {path} -> {self.ip_file}")
                    self._verify_ip_file(self.ip_file)
                    return
                except Exception as e:
                    logger.error(f"复制IP文件失败: {str(e)}")
        
        # 还是找不到，创建一个基本的
        logger.warning(f"未找到现有IP文件，创建一个基本的Cloudflare IP列表在 {self.ip_file}")
        self._create_default_ip_file()
        
        # 同样处理IPv6文件
        if self.config.get("cloudflare", {}).get("ipv6", False):
            self._ensure_ipv6_file()
    
    def _verify_ip_file(self, file_path: str):
        """验证IP文件是否有效"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                line_count = len(content.splitlines())
                logger.info(f"IP文件内容长度: {len(content)} 字节, {line_count} 行")
                if len(content) < 10 or line_count < 2:
                    logger.warning(f"IP文件内容可能无效，将创建默认IP文件")
                    self._create_default_ip_file()
        except Exception as e:
            logger.error(f"读取IP文件失败: {str(e)}")
            self._create_default_ip_file()
    
    def _create_default_ip_file(self):
        """创建默认的IP文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.ip_file), exist_ok=True)
            
            with open(self.ip_file, "w") as f:
                f.write("# Cloudflare IP Ranges\n")
                f.write("# From: https://www.cloudflare.com/ips/\n")
                f.write("1.1.1.0/24\n")  # Cloudflare DNS
                f.write("1.0.0.0/24\n")  # Cloudflare DNS
                f.write("104.16.0.0/12\n")  # Cloudflare CDN
                f.write("172.64.0.0/13\n")  # Cloudflare CDN
                f.write("173.245.48.0/20\n")  # Cloudflare
                f.write("103.21.244.0/22\n")  # Cloudflare
                f.write("103.22.200.0/22\n")  # Cloudflare
                f.write("103.31.4.0/22\n")  # Cloudflare
                f.write("141.101.64.0/18\n")  # Cloudflare
                f.write("108.162.192.0/18\n")  # Cloudflare
                f.write("190.93.240.0/20\n")  # Cloudflare
                f.write("188.114.96.0/20\n")  # Cloudflare
                f.write("197.234.240.0/22\n")  # Cloudflare
                f.write("198.41.128.0/17\n")  # Cloudflare
                f.write("162.158.0.0/15\n")  # Cloudflare
                f.write("104.16.0.0/13\n")  # Cloudflare
                f.write("104.24.0.0/14\n")  # Cloudflare
            
            # 输出文件信息
            if os.path.exists(self.ip_file):
                file_size = os.path.getsize(self.ip_file)
                logger.info(f"成功创建IP文件: {self.ip_file}, 大小: {file_size} 字节")
                with open(self.ip_file, 'r') as f:
                    lines = f.readlines()
                    logger.info(f"IP文件包含 {len(lines)} 行")
            else:
                logger.error(f"IP文件创建失败: {self.ip_file}")
        except Exception as e:
            logger.error(f"创建IP文件失败: {str(e)}")
    
    def _ensure_ipv6_file(self):
        """确保IPv6文件存在"""
        logger.info(f"确保IPv6文件存在: {self.ipv6_file}")
        
        if os.path.exists(self.ipv6_file):
            logger.info(f"IPv6文件已存在: {self.ipv6_file}")
            return
        
        # 在可执行文件目录下查找
        bin_dir_ipv6_file = os.path.join(self.bin_dir, "ipv6.txt")
        if os.path.exists(bin_dir_ipv6_file):
            try:
                shutil.copy(bin_dir_ipv6_file, self.ipv6_file)
                logger.info(f"已复制IPv6文件: {bin_dir_ipv6_file} -> {self.ipv6_file}")
                return
            except Exception as e:
                logger.error(f"复制IPv6文件失败: {str(e)}")
        
        # 在其他位置查找，支持架构自适应
        # 获取架构目录
        arch_dir = self._get_arch_dir()
        
        possible_paths = [
            os.path.join(self.base_dir, arch_dir, "ipv6.txt"),
            "/usr/local/bin/ipv6.txt",
            "/usr/local/share/CloudflareST/ipv6.txt",
            "/app/ipv6.txt"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    shutil.copy(path, self.ipv6_file)
                    logger.info(f"已复制IPv6文件: {path} -> {self.ipv6_file}")
                    return
                except Exception as e:
                    logger.error(f"复制IPv6文件失败: {str(e)}")
        
        # 创建一个基本的IPv6文件
        try:
            with open(self.ipv6_file, "w") as f:
                f.write("# Cloudflare IPv6 Ranges\n")
                f.write("# From: https://www.cloudflare.com/ips/\n")
                f.write("2400:cb00::/32\n")
                f.write("2405:8100::/32\n")
                f.write("2606:4700::/32\n")
                f.write("2803:f800::/32\n")
                f.write("2a06:98c0::/29\n")
                f.write("2c0f:f248::/32\n")
            
            logger.info(f"成功创建IPv6文件: {self.ipv6_file}")
        except Exception as e:
            logger.error(f"创建IPv6文件失败: {str(e)}")
    
    def run(self):
        """运行CloudflareSpeedTest（支持并行双栈优选）"""
        if self.running:
            logger.warning("CloudflareSpeedTest已在运行中，跳过本次执行")
            return False

        try:
            self.running = True
            cloudflare_config = self.config.get("cloudflare", {})
            ipv6_enabled = cloudflare_config.get("ipv6", False)
            additional_args = cloudflare_config.get("additional_args", "")

            logger.info(f"开始运行CloudflareSpeedTest（IPv6并行优选: {'启用' if ipv6_enabled else '关闭'}）")

            # 确保可执行文件存在
            if not os.path.exists(self.cft_path):
                msg = f"CloudflareSpeedTest可执行文件不存在: {self.cft_path}"
                logger.error(msg)
                return {"success": False, "logs": [msg]}

            # 确保IP文件就绪
            self._ensure_ip_files()
            if ipv6_enabled:
                self._ensure_ipv6_file()

            all_logs: list = []

            if ipv6_enabled:
                # ── 并行双栈模式 ──────────────────────────────
                import concurrent.futures
                logger.info("[双栈并行] 同时启动 IPv4 / IPv6 测速进程...")
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    future_v4 = executor.submit(
                        self._run_cfst_process, False, self.result_v4_file, additional_args
                    )
                    future_v6 = executor.submit(
                        self._run_cfst_process, True, self.result_v6_file, additional_args
                    )
                    res_v4 = future_v4.result()
                    res_v6 = future_v6.result()

                all_logs.extend(res_v4.get("logs", []))
                all_logs.extend(res_v6.get("logs", []))

                # 解析两份结果，选最优
                best_v4_ip, best_v4_speed = self._parse_best_from_csv(self.result_v4_file)
                best_v6_ip, best_v6_speed = self._parse_best_from_csv(self.result_v6_file)

                logger.info(f"[双栈对比] IPv4最优: {best_v4_ip} ({best_v4_speed:.2f} MB/s)  "
                            f"IPv6最优: {best_v6_ip} ({best_v6_speed:.2f} MB/s)")

                if best_v4_ip is None and best_v6_ip is None:
                    logger.warning("[双栈并行] 两次测速均未获得有效结果")
                    return {"success": False, "logs": all_logs}

                if best_v4_ip and best_v6_ip:
                    # 两种协议都有结果 → 双条并存
                    logger.info(f"[双栈并存] IPv4={best_v4_ip}  IPv6={best_v6_ip}")
                    self._apply_dual_stack_ips(best_v4_ip, best_v6_ip)
                elif best_v4_ip:
                    # 仅 IPv4 有效
                    logger.info("[双栈并行] 仅 IPv4 有效，降级单条写入")
                    self._apply_best_ip(best_v4_ip, best_v4_speed)
                else:
                    # 仅 IPv6 有效
                    logger.info("[双栈并行] 仅 IPv6 有效，降级单条写入")
                    self._apply_best_ip(best_v6_ip, best_v6_speed)

                # 将胜出结果复制为标准 result.csv（供 get_last_result 展示）
                winner_file = self.result_v6_file if (best_v6_speed > best_v4_speed and best_v6_ip) else self.result_v4_file
                if os.path.exists(winner_file):
                    import shutil as _shutil
                    _shutil.copy2(winner_file, self.result_file)

                return {"success": True, "logs": all_logs}

            else:
                # ── 纯 IPv4 模式（原有行为）────────────────────
                res = self._run_cfst_process(False, self.result_file, additional_args)
                all_logs.extend(res.get("logs", []))
                if os.path.exists(self.result_file):
                    self._process_results()
                    logger.info("CloudflareSpeedTest执行完成")
                else:
                    logger.error("CloudflareSpeedTest执行失败，未生成结果文件")
                return {"success": res["success"], "logs": all_logs}

        except Exception as e:
            logger.error(f"运行CloudflareSpeedTest出错: {e}")
            return {"success": False, "logs": [f"错误: {e}"]}
        finally:
            self.running = False
    
    def _process_results(self):
        """处理 IPv4 单次测速结果（兼容旧路径）"""
        best_ip, best_speed = self._parse_best_from_csv(self.result_file)
        if best_ip:
            self._apply_best_ip(best_ip, best_speed)
        else:
            logger.warning("未找到合适的IP")
    
    def get_last_result(self) -> Dict[str, Any]:
        """获取最后一次测试结果"""
        try:
            if not os.path.exists(self.result_file):
                return {"success": False, "message": "尚未执行测试或结果文件不存在"}
            
            # 获取文件修改时间
            modified_time = os.path.getmtime(self.result_file)
            modified_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(modified_time))
            
            # 读取结果文件
            with open(self.result_file, 'r') as f:
                lines = f.readlines()
            
            if len(lines) <= 1:
                return {"success": False, "message": "结果文件中没有有效数据", "time": modified_time_str}
            
            # 解析结果
            headers = lines[0].strip().split(',')
            results = []
            
            for i in range(1, min(11, len(lines))):  # 最多返回前10条
                data = lines[i].strip().split(',')
                if len(data) >= len(headers):
                    result = {}
                    for j, header in enumerate(headers):
                        result[header] = data[j]
                    results.append(result)
            
            return {
                "success": True,
                "time": modified_time_str,
                "results": results
            }
        except Exception as e:
            logger.error(f"获取测试结果出错: {str(e)}")
            return {"success": False, "message": f"获取测试结果出错: {str(e)}"}
    
    def is_running(self) -> bool:
        """检查是否正在运行测试"""
        return self.running 