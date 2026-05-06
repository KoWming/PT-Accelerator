@echo off
:: PT-Accelerator Windows 启动脚本

:: 设置默认端口（可通过环境变量覆盖）
if "%APP_PORT%"=="" set APP_PORT=23333

:: 创建必要目录
if not exist "config" mkdir config
if not exist "logs" mkdir logs
if not exist "cache" mkdir cache
if not exist "CFST" mkdir CFST

:: 安装依赖（首次运行）
if not exist "venv" (
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

:: 启动服务
python main.py
