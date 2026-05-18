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

> 基于 [CloudflareSpeedTest (XIU2)](https://github.com/XIU2/CloudflareSpeedTest) 项目

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

如需修改端口或其他行为，可通过环境变量配置，详见 [🌐 环境变量](#-环境变量) 章节。

## 🔐 管理员离线恢复

当前管理员离线恢复已加固为三重门槛：

1. 必须在服务器本机环境中设置 `ADMIN_RESET_KEY`
2. 必须存在本机恢复令牌文件 `config/.admin_reset_token`
3. 必须通过交互式方式输入两次新密码

### 首次令牌文件生成

- 若你在首次初始化或后续在线改密时已经设置了 `ADMIN_RESET_KEY`，系统会自动：
  - 生成随机本机恢复令牌文件 `config/.admin_reset_token`
  - 将 `ADMIN_RESET_KEY` 的哈希与恢复令牌哈希写入 `config.yaml` 的 `auth.reset_key_hash` / `auth.reset_token_hash`
- 若当时没有设置 `ADMIN_RESET_KEY`，则不会生成离线恢复材料；此时需要先在已登录状态下设置 `ADMIN_RESET_KEY` 并执行一次在线改密，才能完成离线恢复材料绑定
- 一旦完成绑定，后续若 `config/.admin_reset_token` 缺失、被替换，或 `ADMIN_RESET_KEY` 与已绑定值不一致，系统会拒绝离线重置
- 请将该文件与 `config.yaml`、`.secret_key` 一样视为高敏感部署资产，仅允许部署账号读写

### 使用方式

Linux/macOS：

```bash
export ADMIN_RESET_KEY='<16位强随机密钥>'
python main.py --reset-admin --username admin
```

Windows PowerShell：

```powershell
$env:ADMIN_RESET_KEY = '<16位强随机密钥>'
python main.py --reset-admin --username admin
```

执行后程序会交互式提示输入两次新密码；若 `ADMIN_RESET_KEY` 缺失、与已绑定的恢复密钥哈希不一致，或本机恢复令牌文件 `config/.admin_reset_token` 缺失/被替换，离线重置会被拒绝。

## 🐳 Docker 部署

### 使用 Docker Compose

项目已提供 `docker-compose.yml`，默认使用 host 网络模式，端口由 `APP_PORT` 环境变量控制（默认 `23333`）。

可参考以下编排示例：

```yaml
version: "3.8"

services:
  pt-accelerator:
    image: kowming/pt-accelerator:new
    container_name: pt-accelerator-new
    restart: unless-stopped
    network_mode: host
    volumes:
      - /etc/hosts:/etc/hosts  #必须，用于 Hosts 联动功能
      - ./CFST:/app/CFST
      - ./config:/app/config
      - ./logs:/app/logs
      - ./cache:/app/cache
    environment:
      - TZ=Asia/Shanghai
      - APP_PORT=23333
      - ADMIN_RESET_KEY=<16位强随机密钥> #建议设置，启用管理员离线恢复功能
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:$$APP_PORT/api/health"]
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

可通过环境变量配置应用行为，完整说明见 [🌐 环境变量](#-环境变量) 章节。

Docker 部署常用环境变量：

- `APP_PORT=23333` — 应用监听端口
- `ADMIN_RESET_KEY=<16位强随机密钥>` — 管理员离线恢复密钥
- `TZ=Asia/Shanghai` — 容器时区

容器健康检查接口：

- `/api/health`

### 使用 docker run

如果你不使用 Compose，也可以直接运行：

```bash
docker run -d \
	--name pt-accelerator-new \
	--restart unless-stopped \
	--network host \
	-e TZ=Asia/Shanghai \
	-e APP_PORT=23333 \
	-e ADMIN_RESET_KEY=<16位强随机密钥> \
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

## 🌐 环境变量

| 变量名 | 默认值 | 必需 | 说明 |
|--------|--------|------|------|
| `APP_PORT` | `23333` | 否 | 应用监听端口 |
| `ADMIN_RESET_KEY` | _(空)_ | 离线重置时必需 | 管理员离线恢复密钥，用于三重校验绑定与离线重置授权；生产环境建议固定设置并妥善保管 |
| `APP_SECRET_KEY` | 自动生成 | 否 | 敏感配置加密密钥（AES-128-GCM），用于加密 config.yaml 中的密码、Token 等敏感字段；未设置时自动生成并存储到 `config/.secret_key` |
| `CONFIG_DIR` | `config` | 否 | 配置文件目录路径 |
| `COOKIE_SECURE` | `false` | 否 | 启用 Cookie Secure 标记，HTTPS 部署时建议开启（`true` / `1` / `yes`） |
| `ALLOW_REMOTE_INIT` | `false` | 否 | 允许远程 IP 进行首次管理员初始化，默认仅限本机（`true` / `1` / `yes`），**不建议在生产环境开启** |
| `LOGIN_MAX_FAILURES` | `5` | 否 | 同一 IP 连续登录失败次数上限，超出后触发锁定 |
| `LOGIN_LOCKOUT_SECONDS` | `300` | 否 | 登录锁定持续时间（秒），锁定期间该 IP 无法尝试登录 |
| `CORS_ORIGINS` | _(空)_ | 否 | 额外允许的 CORS 来源，多个用逗号分隔（如 `https://a.com,https://b.com`） |
| `ENABLE_OPENAPI_DOCS` | `false` | 否 | 启用 OpenAPI 文档（`/docs`、`/redoc`），生产环境不建议开启（`true` / `1` / `yes`） |
| `EXTRA_HOSTS_PATHS` | _(空)_ | 否 | 额外允许写入的 Hosts 文件路径，多个用分号分隔（如 `/custom/hosts1;/custom/hosts2`） |
| `TRUSTED_PROXY_IPS` | _(空)_ | 否 | 受信任反向代理 IP 白名单，多个用英文逗号分隔。仅当直连来源属于该白名单时，后端才会解析 `X-Forwarded-For` / `X-Real-IP`；未设置时默认只信任直连客户端 IP |
| `TZ` | 系统默认 | Docker 部署建议设置 | 容器时区（如 `Asia/Shanghai`），影响日志时间戳与通知时间 |

### 环境变量说明

- **布尔类型**变量接受 `true` / `1` / `yes`（不区分大小写）为真值，其余为假
- **`APP_SECRET_KEY`** 支持 Base64 编码格式或原始字符串（取前 16 字节用于 AES-128）；生产环境建议通过环境变量固定设置，避免自动生成的密钥文件丢失后无法解密已有配置
- **`ADMIN_RESET_KEY`** 仅在需要使用离线管理员重置功能时必须设置；设置后需在已登录状态下完成一次在线改密，系统才会绑定恢复材料到 config.yaml
- **`TRUSTED_PROXY_IPS`** 用于声明哪些反向代理来源可被信任；只有这些来源转发的 `X-Forwarded-For` / `X-Real-IP` 才会参与客户端 IP 判定，避免被客户端伪造请求头绕过初始化来源限制或登录限流
- 登录成功后当前版本**仅依赖 HttpOnly Cookie 维持会话**，不再返回可复用的 session token

## ⚙️ 配置说明

### 配置目录

- `config/config.yaml`：主配置文件
- `config/trackers.yaml`：Tracker / Cloudflare 域名名单配置
- `config/.schema_version`：配置结构版本标记
- `config/.secret_key`：敏感配置加密密钥文件，用于解密 `config.yaml` 中的密码、Token 等敏感字段
- `config/.auth_initialized`：认证初始化状态标记文件，用于辅助判断当前部署是否已完成管理员初始化
- `config/.admin_reset_token`：本机离线恢复令牌文件，离线管理员重置必需，请视为高敏感部署资产妥善保存

首次启动时，程序会自动初始化默认配置。

### 配置备份建议

建议至少同时备份以下文件：

- `config/config.yaml`
- `config/trackers.yaml`
- `config/.secret_key`
- `config/.admin_reset_token`

说明：

- 系统自动备份当前仅包含 `config/config.yaml`，不会自动备份其他敏感文件，请自行妥善保管 `config/.secret_key`、`config/.admin_reset_token` 等部署安全材料
- 若只备份 `config.yaml` 而未备份 `config/.secret_key`，可能导致历史敏感配置无法解密
- 若已绑定离线恢复材料但缺失 `config/.admin_reset_token`，离线管理员重置会被拒绝
- `config/.auth_initialized` 与 `config/.schema_version` 通常可自动重建，但保留备份更稳妥

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

当前项目版本：`3.0.6`

### 更新日志

#### v3.0.6 (2026-05-18)

**🔐 配置文件敏感字段加密迁移**
- 新增配置 schema 版本管理（v1 → v2），首次启动时自动将旧配置中的明文敏感字段加密为 `enc:` 格式
- 覆盖加密字段：`ikuai.password`、`backup.webdav_password`、`downloaders.items[*].password/apikey`、以及 `notify.channels` 中全部 16 类敏感配置
- 加密采用 AES-GCM 体系，密钥派生自自动生成的 `.secret_key` 文件（首次加密时自动创建）
- 迁移过程幂等安全：已加密字段（`enc:` 前缀）不再重复加密；加密失败时保留原值并记录警告，不破坏配置文件
- 迁移完成后自动将 `schema_version` 更新为 2，后续启动不再重复执行迁移

#### v3.0.5 (2026-05-17)

**🔐 认证与会话安全**
- 管理员登录改为单会话模式：同一账号新登录会自动撤销旧会话
- 管理员修改密码后会立即撤销该账号全部旧会话，强制重新登录
- 登录态校验改为仅信任 HttpOnly Cookie，不再兼容通过响应体或 `Authorization` 传递会话 ID
- 登录成功响应不再返回 `token=session_id`，收敛会话标识暴露面
- 启动时存在 0 个本地会话时不再输出无意义日志

**🛡️ 请求防护与响应加固**
- 为所有基于 Cookie 会话的写接口统一补齐 CSRF 校验，覆盖认证、备份、CFST、下载器、Hosts、爱快、小米路由器、通知、调度器、Tracker、日志清理等状态变更操作
- 前端 `axios` 统一接入 CSRF：自动获取 `csrf_token`，并为 `POST` / `PUT` / `PATCH` / `DELETE` 请求自动注入 `X-CSRF-Token`
- `/api/settings/config` 配置脱敏递归增强：补齐 `list` 结构递归处理，并覆盖 `apikey` 等敏感字段，避免密文/明文敏感配置回显到前端
- 后端统一补充基础安全响应头：`Content-Security-Policy`、`X-Frame-Options`、`X-Content-Type-Options`、`Referrer-Policy`、`Permissions-Policy`
- 前端所有 `target="_blank"` 外链统一补齐 `rel="noopener noreferrer"`

**🌐 网络与敏感数据安全**
- `get_client_ip()` 改为默认仅信任直连来源 IP，只有在配置 `TRUSTED_PROXY_IPS` 后才解析 `X-Forwarded-For` / `X-Real-IP`
- 敏感配置写入改为 fail-closed：缺少 `cryptography` 或加密失败时拒绝写入，不再静默降级到 XOR/明文；旧版 XOR 数据仍保留解密兼容
- Cloudflare HTTP 探测恢复 TLS 证书校验，移除 `verify=False`

**🧰 离线恢复与文档完善**
- 管理员离线重置收紧为“三重门槛”：`ADMIN_RESET_KEY`、本机恢复令牌文件、交互式二次密码确认缺一不可
- 离线管理员重置 CLI 的预期失败改为错误日志输出，不再直接抛 traceback
- 为离线管理员重置失败日志统一增加 `[offline-reset]` 前缀，便于检索与告警
- README 新增环境变量章节，补充 `APP_SECRET_KEY`、`ADMIN_RESET_KEY`、`TRUSTED_PROXY_IPS`、`COOKIE_SECURE`、`ALLOW_REMOTE_INIT` 等说明

<details>
<summary>查看历史更新日志</summary>

#### v3.0.4 (2026-05-12)

**✨ 功能优化**
- 适配qbittorrent 5.0.0 及以上版本的 API 变更，更新下载器连接逻辑
- 下载器连接层统一适配新版 `qbittorrent-api` 与 `transmission-rpc` 依赖
- `qBittorrent` 新增 API Key 认证支持，兼容新版 WebUI 鉴权方式
- 清理 Transmission 旧版兼容逻辑，仅保留基于最新依赖的实现
- 优化 `start.bat` 与 `start.sh` 启动脚本，统一为 `python main.py` 入口并增强启动日志展示

#### v3.0.3 (2026-05-12)

**🐛 Bug 修复**
- 修复 CFST 设置中的测速 URL 留空后仍被自动写回默认地址的问题
- 修复应用升级后 `config.yaml` 中 `app.version` 不会自动同步到当前程序版本的问题
- 修复前端版本获取失败时仍显示过期 fallback 版本号的问题

**✨ 功能优化**
- Cloudflare 域名名单迁移到 `config/trackers.yaml` 中统一存储，不再保留 `config.yaml` 的 `cloudflare_domains` 字段
- Cloudflare 域名名单中的域名即使不是 Tracker，也可在 CFST 优选后写入系统 Hosts
- 优化 `IP优选与Hosts更新` 通知样式，补充 Hosts 源统计、探测成功数、失败兜底数与失败兜底域名展示
- 优化 `CFST测速` 单独通知语义，在跳过 Hosts 更新或执行失败时展示更明确的状态与原因

#### v3.0.2 (2026-05-10)

**🐛 Bug 修复**
- 修复 Server酱通知发送失败（title 为空导致 API 400 错误）
- 修复通知标题重复显示问题（title 和 body 同时包含标题）
- 修复 `PUT /api/trackers/ip` 接口 500 错误（缺少 `update_all_trackers_ip` 方法）
- 修复 Cloudflare 域名名单更新后 tracker 的 `is_cloudflare` 标记未同步的问题

**✨ 功能优化**
- Cloudflare 域名名单新增「当前 IP」列显示
- 通知渠道开关操作新增 Toast 提示反馈
- `list_enabled_cloudflare` 运行时检查白名单，白名单域名无需网络检测直接生效

**🐳 Docker 优化**
- 添加 `TZ=Asia/Shanghai` 环境变量，修复容器日志和通知时间偏差 8 小时
- 改用 `network_mode: host`，移除端口映射
- 健康检查改用 `CMD-SHELL`，端口统一由 `APP_PORT` 变量控制

**💄 UI 优化**
- 移动端 Cloudflare 域名名单：IP 与域名显示在同一行

#### v3.0.1 (2026-05-07)
 
**🐛 Bug 修复**
- 修复定时任务 Cron 表达式时区偏移问题

**💄 UI 优化**
- 优化移动端 UI 显示效果，改善小屏设备下的布局适配与交互体验

</details>

## 📄 许可证

本项目基于 **MIT License** 开源发布。

许可证全文请见：`LICENSE`
