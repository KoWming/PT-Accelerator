#!/bin/bash
# PT-Accelerator Linux/macOS 启动脚本

set -e

APP_PORT=${APP_PORT:-23333}

# 创建必要目录
mkdir -p config logs cache CFST

# 安装依赖（首次运行）
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

# 启动服务
python -m uvicorn main:app --host 0.0.0.0 --port $APP_PORT --reload
