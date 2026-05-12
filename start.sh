#!/bin/bash
# PT-Accelerator Linux/macOS 启动脚本

set -e

APP_PORT=${APP_PORT:-23333}

echo "=================================================="
echo "              PT-Accelerator 启动器"
echo "=================================================="
echo "[平台] Linux/macOS"
echo "[目录] $(pwd)"
echo

if ! command -v python3 >/dev/null 2>&1; then
    echo "[错误] 未找到 python3，请先安装 Python 3.10+。"
    exit 1
fi

# 创建必要目录
echo "[步骤 1/4] 准备运行目录..."
mkdir -p config logs cache CFST
echo "[完成] 运行目录已就绪"
echo

# 创建虚拟环境（首次运行）
echo "[步骤 2/4] 检查 Python 虚拟环境..."
if [ ! -d "venv" ]; then
    echo "[信息] 正在创建虚拟环境..."
    python3 -m venv venv
    echo "[完成] 虚拟环境创建成功"
else
    echo "[完成] 已检测到现有虚拟环境"
fi

source venv/bin/activate
echo

# 安装或更新依赖
echo "[步骤 3/4] 安装或更新依赖..."
python -m pip install -r requirements.txt
echo "[完成] 依赖已准备就绪"
echo

LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || true)
fi
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="127.0.0.1"
fi

# 启动服务（统一走项目主入口）
echo "[步骤 4/4] 启动应用服务..."
echo "--------------------------------------------------"
echo "[端口] ${APP_PORT}"
echo "[本机] http://127.0.0.1:${APP_PORT}"
echo "[局域网] http://${LOCAL_IP}:${APP_PORT}"
echo "--------------------------------------------------"
echo
python main.py
