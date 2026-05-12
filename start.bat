@echo off
setlocal
:: PT-Accelerator Windows 启动脚本

echo ==================================================
echo               PT-Accelerator 启动器
echo ==================================================
echo [平台] Windows
echo [目录] %CD%
echo.

:: 设置默认端口（可通过环境变量覆盖）
if "%APP_PORT%"=="" set APP_PORT=23333

:: 检查 Python 是否可用
where python >nul 2>nul
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+ 并加入 PATH。
    exit /b 1
)

:: 创建必要目录
echo [步骤 1/4] 准备运行目录...
if not exist "config" mkdir config
if not exist "logs" mkdir logs
if not exist "cache" mkdir cache
if not exist "CFST" mkdir CFST
echo [完成] 运行目录已就绪
echo.

:: 创建虚拟环境（首次运行）
echo [步骤 2/4] 检查 Python 虚拟环境...
if not exist "venv" (
    echo [信息] 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败。
        exit /b 1
    )
    echo [完成] 虚拟环境创建成功
 ) else (
    echo [完成] 已检测到现有虚拟环境
)
echo.

:: 激活虚拟环境
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 激活虚拟环境失败。
    exit /b 1
)

:: 安装或更新依赖
echo [步骤 3/4] 安装或更新依赖...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 安装依赖失败。
    exit /b 1
)
echo [完成] 依赖已准备就绪
echo.

set "LOCAL_IP=127.0.0.1"
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /R /C:"IPv4.*:"') do (
    for /f "tokens=* delims= " %%j in ("%%i") do (
        set "LOCAL_IP=%%j"
        goto :ip_found
    )
)
:ip_found

:: 启动服务（统一走项目主入口）
echo [步骤 4/4] 启动应用服务...
echo --------------------------------------------------
echo [端口] %APP_PORT%
echo [本机] http://127.0.0.1:%APP_PORT%
echo [局域网] http://%LOCAL_IP%:%APP_PORT%
echo --------------------------------------------------
echo.
python main.py
exit /b %errorlevel%
