# 🚀 PT-Accelerator-New

面向 PT 场景的连接优化、追踪器管理、下载器同步与 Hosts / DNS 联动平台。

## 📖 项目简介

`PT-Accelerator-New` 基于 `FastAPI + Vue 3` 构建，提供统一的 Web 控制台，用于管理 PT 常见的网络优化与自动化任务，包括：

- CFST 测速与优选
- Tracker 列表维护与同步
- qBittorrent / Transmission 下载器管理
- 本地 Hosts 更新与路由器 DNS 联动
- 定时任务调度
- 通知推送
- 配置备份与恢复
- 日志查看与系统设置

项目默认通过浏览器访问，无需单独部署前端服务。

## 🔄 迁移说明

- **暂不支持**使用旧版本配置文件直接覆盖新版本配置
- 建议先单独部署 `PT-Accelerator-New` 容器并完成初始化
- 待新版本运行正常后，再手动迁移旧版本配置到新版本**各项设置中**
- 确认新版本配置与功能均正常后，再删除旧版本容器

## ✨ 核心功能

### 1. ⚡ CFST 加速管理

- 启动时自动检测 CFST 二进制
- 缺失时尝试自动安装
- 支持测速任务配置与结果管理
- 可配合定时任务自动执行

### 2. 🧭 Tracker 管理

- 统一维护 Tracker 数据
- 支持更新、检测与同步流程
- 可与下载器配置联动

### 3. 📦 下载器管理

- 支持 `qBittorrent` 与 `Transmission`
- 支持多客户端配置
- 统一保存连接参数与启用状态

### 4. 🌐 Hosts / DNS 联动

- 支持本地 Hosts 更新
- 支持备份原有 Hosts 内容
- 支持与爱快、部分小米路由器 DNS 配置联动

### 5. 💾 备份与恢复

- 支持本地配置备份
- 支持历史备份查看、恢复、删除
- 支持 WebDAV 远程上传

### 6. ⏰ 通知与调度

- 基于 `APScheduler` 的定时任务机制
- 支持任务异常与执行结果通知
- 支持多类业务任务统一调度

### 7. 🖥️ Web 控制台

- 前端基于 `Vue 3 + Vite + TypeScript`
- 提供认证、设置、日志、任务等可视化界面
- 后端统一以 `/api` 提供接口

## 🛠️ 技术栈

### 后端

- Python 3.12+
- FastAPI
- Uvicorn
- APScheduler
- Pydantic
- PyYAML
- httpx

### 前端

- Vue 3
- TypeScript
- Vite
- Pinia
- Axios
- Bootstrap 5
- Sass

## 📁 目录结构

```text
PT-Accelerator-New/
├─ app/                 后端主程序
│  ├─ routes/           API 路由
│  ├─ services/         核心业务服务
│  ├─ pipelines/        自动化处理流程
│  ├─ utils/            工具模块
│  ├─ config.py         配置管理
│  ├─ main.py           FastAPI 应用入口
│  └─ models.py         数据模型定义
├─ frontend/            前端源码
├─ config/              配置目录
├─ logs/                日志目录
├─ cache/               缓存目录
├─ CFST/                CFST 相关文件目录
├─ Dockerfile           容器构建文件
├─ docker-compose.yml   容器编排文件
├─ requirements.txt     Python 依赖
├─ main.py              项目启动入口
├─ start.bat            Windows 启动脚本
├─ start.sh             Linux/macOS 启动脚本
└─ version.py           版本信息
```

## 🚀 快速开始

### 📋 运行要求

- Python 3.12 或更高版本
- Node.js 18+（仅前端开发或手动构建前端时需要）
- Windows / Linux / macOS

## ▶️ 本地运行

### 🪟 Windows

项目根目录执行：

`start.bat`

脚本会自动完成以下操作：

- 创建 `venv` 虚拟环境
- 安装 `requirements.txt` 依赖
- 创建 `config`、`logs`、`cache`、`CFST` 目录
- 启动后端服务

### 🐧 Linux / macOS

项目根目录执行：

`bash start.sh`

### 🔧 手动启动

如果你希望自行控制环境，可在项目根目录执行：

1. 创建虚拟环境并安装依赖
2. 运行 `python main.py`

应用默认监听端口：`23333`

如需修改端口，可设置环境变量 `APP_PORT`。

## 🐳 Docker 部署

### 使用 Docker Compose

项目已提供 `docker-compose.yml`，默认映射端口为 `23333`。

可参考以下编排示例：

```yaml
version: "3.8"

services:
  pt-accelerator:
    image: kowming/pt-accelerator:new
    container_name: pt-accelerator-new
    restart: unless-stopped
    ports:
      - "23333:23333"
    volumes:
      - /etc/hosts:/etc/hosts  #必须，用于 Hosts 联动功能
      - ./CFST:/app/CFST
      - ./config:/app/config
      - ./logs:/app/logs
      - ./cache:/app/cache
    environment:
      - APP_PORT=23333
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:23333/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

启动命令：

```bash
docker compose up -d
```

主要挂载目录：

- `/etc/hosts:/etc/hosts`  #必须，用于 Hosts 联动功能
- `./CFST:/app/CFST`       #CFST 二进制与相关文件
- `./config:/app/config`   #配置文件
- `./logs:/app/logs`       #运行日志
- `./cache:/app/cache`     #缓存数据

可通过环境变量覆盖端口：

- `APP_PORT=23333`

容器健康检查接口：

- `/api/health`

### 使用 docker run

如果你不使用 Compose，也可以直接运行：

```bash
docker run -d \
	--name pt-accelerator-new \
	--restart unless-stopped \
	-p 23333:23333 \
	-e APP_PORT=23333 \
	-v /etc/hosts:/etc/hosts \
	-v ./CFST:/app/CFST \
	-v ./config:/app/config \
	-v ./logs:/app/logs \
	-v ./cache:/app/cache \
	kowming/pt-accelerator:new
```

如需本地构建镜像，可执行：

```bash
docker build -t pt-accelerator:new .
```

### Docker 构建特点

- 使用多阶段构建
- 前端在构建阶段自动打包
- 后端镜像基于 `python:3.12-slim`

## 🔗 访问入口

启动成功后，可访问：

- 前端页面：`http://localhost:23333`
- 健康检查：`http://localhost:23333/api/health`
- OpenAPI 文档：`http://localhost:23333/docs`

## 🧩 主要接口模块

后端接口统一挂载在 `/api` 下，主要包含：

- `/api/auth`：登录、登出、CSRF、状态
- `/api/cfst`：CFST 配置、执行、结果
- `/api/trackers`：Tracker 管理
- `/api/clients`：下载器管理
- `/api/hosts`：Hosts 管理
- `/api/ikuai`：爱快联动
- `/api/mihosts`：小米路由器联动
- `/api/scheduler`：定时任务管理
- `/api/notify`：通知渠道配置
- `/api/backup`：备份与恢复
- `/api/logs`：日志查看
- `/api/settings`：系统设置

## ⚙️ 配置说明

### 配置目录

- `config/config.yaml`：主配置文件
- `config/.schema_version`：配置结构版本标记

首次启动时，程序会自动初始化默认配置。

### 数据目录用途

| 目录 | 用途 |
| --- | --- |
| `/etc/hosts` | 必须挂载，用于 Hosts 联动功能 |
| `config/` | 配置文件与配置版本信息 |
| `logs/` | 运行日志 |
| `cache/` | 缓存数据 |
| `CFST/` | CFST 二进制、测速相关文件 |

## 🧪 开发说明

### 前端开发

前端源码位于 `frontend/`，技术栈为 `Vite + Vue 3 + TypeScript`。

常见流程：

1. 安装前端依赖
2. 在 `frontend/` 下启动开发服务
3. 构建后生成 `frontend/dist`

生产环境下，后端会优先加载 `frontend/dist`，并自动处理 SPA 路由回退。

### 后端开发

- Web 应用实例位于 `app/main.py`
- 项目统一启动入口位于根目录 `main.py`
- 调试模式下可启用自动重载

## ⚠️ 注意事项

- CFST 不存在时，程序会尝试自动安装；失败后可手动放入 `CFST/` 目录
- 修改本地 Hosts 通常需要管理员或 root 权限
- 默认端口为 `23333`，如端口冲突请修改 `APP_PORT`
- 首次启动会自动创建配置与运行目录
- Docker 部署下不依赖单独启动前端服务

## 🏷️ 版本信息

当前项目版本：`3.0.1`

### 更新日志

#### v3.0.1 (2025-05-07)

**🐛 Bug 修复**
- 修复定时任务 Cron 表达式时区偏移问题

**💄 UI 优化**
- 优化移动端 UI 显示效果，改善小屏设备下的布局适配与交互体验

## 📄 许可证

本项目基于 **MIT License** 开源发布。

许可证全文请见：`LICENSE`
