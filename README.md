# PT-Accelerator v2.2.3

一个面向PT站点用户的全自动加速与管理平台，采用 **Vue 3 + FastAPI** 前后端分离架构。集成Cloudflare IP优选、PT Tracker批量管理、GitHub/TMDB等站点加速、下载器一键导入、Web可视化配置等多种功能，支持Docker一键部署，适合所有对网络加速和PT站点体验有高要求的用户。

---

## 功能亮点

- **Cloudflare IP优选**：自动筛选更快的 Cloudflare IP，提升 PT 站点与 GitHub 等访问速度。
- **Tracker 高效管理**：支持批量增删、状态切换、下载器导入与 Cloudflare 站点筛选。
- **Hosts 智能合并**：内置多条 GitHub/TMDB Hosts 源，支持合并、去重、优选与在线编辑。
- **下载器集中接入**：兼容 qBittorrent、Transmission 等主流下载器，支持多实例统一管理。
- **可视化控制面板**：基于 **Vue 3 + FastAPI**，统一管理任务、日志、白名单、配置与通知。
- **一键清理重建**：支持一键清空 Tracker、清空并重建 Hosts，减少历史污染影响。
- **多渠道通知**：任务完成与异常状态可通过多种通知方式及时推送。
- **跨平台部署**：支持 Docker 与原生 Python 环境，兼容 AMD64、ARM64 及主流桌面/服务器系统。

---

## 快速开始

### 1. Docker一键部署（推荐）

Docker镜像已包含构建好的前端资源，开箱即用。
建议使用Vue 3构建的版本(旧版本镜像已不再更新)，版本标签为 latest-dev (支持自适应架构X86/arm64)

```bash
# 自动选择架构（推荐）
docker run -d \
  --name pt-accelerator \
  --network host \
  -v /etc/hosts:/etc/hosts \
  -v /path/to/config:/app/config \
  -v /path/to/logs:/app/logs \
  -e TZ=Asia/Shanghai \
  kowming/pt-accelerator:latest-dev
```

或使用`docker-compose.yml`：

```yaml
services:
  pt-accelerator:
    image: kowming/pt-accelerator:latest-dev
#    image: eternalcurse/pt-accelerator:latest
    container_name: pt-accelerator
    restart: unless-stopped
    network_mode: host
    environment:
      - TZ=Asia/Shanghai
    volumes:
      - /etc/hosts:/etc/hosts
      - ./config:/app/config
      - ./logs:/app/logs
```

创建上述`docker-compose.yml`文件后，在同一目录下运行：

```bash
docker-compose up -d
```

### 2. 本地运行（开发/调试）

本项目采用前后端分离架构，本地运行需要分别构建前端和启动后端。

**前置要求**：
- Node.js 20+
- Python 3.11+

#### 步骤一：构建前端 (Vue 3)

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 构建生产环境资源 (生成 dist 目录)
npm run build

# 返回项目根目录
cd ..
```

#### 步骤二：启动后端 (FastAPI)

后端会自动挂载前端构建生成的 `frontend/dist` 目录。

```bash
# 安装后端依赖
pip install -r requirements.txt

# 启动服务
bash start.sh
# 或手动运行
# python -m uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT:-23333}
```

#### 开发模式 (热重载)

如果你需要修改前端代码，建议同时开启前后端开发服务器：

1.  **启动后端**：
    ```bash
    python -m uvicorn app.main:app --host 0.0.0.0 --port 23333 --reload
    ```
2.  **启动前端 (Vite)**：
    ```bash
    cd frontend
    npm run dev
    ```
    访问 Vite 提供的开发地址 (通常是 `http://localhost:5173`) 进行调试。

---

## Web界面入口

- 访问：http://your-ip:<端口号>
- 首次访问或根据配置，可能需要进行用户登录。
- 默认端口：`23333`。可以通过以下方式修改：
  - **Docker/Docker Compose**:
    - 在 `docker-compose.yml` 文件中，为 `pt-accelerator` 服务的 `environment` 部分添加或修改 `APP_PORT` 的值。例如:
      ```yaml
      services:
        pt-accelerator:
          # ... other settings ...
          environment:
            - TZ=Asia/Shanghai
            - APP_PORT=8080 # 设置自定义端口
      ```
    - 或者，在 `docker-compose.yml` 同级目录下创建 `.env` 文件并写入 `APP_PORT=8080`，这会覆盖 `docker-compose.yml` 中的默认设置（如果存在）。
  - **本地运行**: 启动前设置 `APP_PORT` 环境变量 (例如 `export APP_PORT=8080 && bash start.sh`)，或者直接修改 `start.sh` 脚本中的默认端口。
- 支持多用户同时操作，所有配置实时生效

---

## 主要功能模块

- 查看调度器状态、定时任务列表，一键触发 IP 优选与 Hosts 更新
- 一键仅更新 Hosts（沿用上次优选 IP，不重新测速）
- 一键清空并重建（仅移除项目写入分区，系统原有内容不受影响）
- 配置 CRON 定时任务，保存后立即生效

### 2. Tracker 管理
- 批量添加、批量清空、单个删除、状态切换
- 一键从下载器导入 Tracker（自动筛选 Cloudflare 站点）
- Cloudflare 白名单管理、Tracker IP 一键批量更新

### 3. Hosts 源管理
- 多条外部 Hosts 源自动合并、去重、优选（延迟最低原则）
- 支持添加、删除、启用/禁用 Hosts 源
- 内置 GitHub/TMDB 加速 Hosts 源，自动定时更新

### 4. 下载器管理
- 支持多个 qBittorrent / Transmission 实例，各自独立配置
- 一键测试连接、保存配置、导入 Tracker
- 支持 HTTPS、端口、用户名密码等完整配置

### 5. 日志与监控
- 实时查看系统日志、任务进度，支持自动滚动与一键清空

### 6. Hosts 文件管理
- 在线编辑 Hosts 文件，实时预览、保存，保护系统原有结构

### 7. 通知系统
- 统一格式推送（`【标题】` + emoji + 分隔符），支持一言日报尾缀
- **支持渠道**：Telegram、企业微信、SMTP、Bark、WxPusher、Gotify、MediaSaber、Webhook

### 8. 备份与恢复
- WebDAV 自动备份（坚果云、Nextcloud 等），支持一键恢复、版本控制

## CloudflareSpeedTest说明

- 已内置CloudflareST二进制和测速脚本，自动调用，无需手动操作
- **架构自适应**：自动检测系统架构（AMD64/ARM64），选择对应的可执行文件和配置文件
- 相关参数和测速数据文件（ip.txt/ipv6.txt）可在对应架构目录下自定义：
  - AMD64架构：`cfst_linux_amd64/` 目录
  - ARM64架构：`cfst_linux_arm64/` 目录
- 自动筛选延迟低、速度快的优质CF节点IP
- 支持IPv4/IPv6双协议测速
- Docker构建时自动排除不需要的架构文件，优化镜像大小
- 参考：https://github.com/XIU2/CloudflareSpeedTest

---

## 常见问题

- **Q: 为什么要挂载/etc/hosts？**  
  A: 程序需要直接更新系统 `hosts` 文件以实现加速，因此必须具备写入权限。

- **Q: 如何彻底清空tracker或hosts？**  
  A: 可在 Web 界面使用“清空所有 Tracker”和“清空 Hosts 并重建”功能快速处理。

- **Q: 日志和配置如何持久化？**  
  A: 建议将 `/app/config` 和 `/app/logs` 挂载到宿主机目录，避免容器重启后数据丢失。

- **Q: 如果系统使用了代理，会影响IP测速吗？**  
  A: 会。建议测速时临时关闭系统代理，以获得更准确的结果。

- **Q: 项目如何更新？**  
  A: Docker 部署可先拉取最新镜像，再重新创建容器完成更新。

- **Q: 支持哪些架构？**  
  A: 支持 AMD64 和 ARM64，包括 x86_64 服务器、树莓派及 ARM 设备，Docker 会自动匹配镜像。

- **Q: 支持哪些通知方式？**  
  A: 支持多种通知渠道，可在配置页面按需设置发送方式与频率。

- **Q: 清空Hosts会破坏系统配置吗？**  
  A: 不会。系统会保留原有 Hosts 头部结构，仅清理 PT-Accelerator 写入的内容。

- **Q: 如何让Docker容器化的下载器（如qBittorrent）使用优化后的hosts？**  
  A: 需要在下载器容器中显式挂载宿主机 `hosts` 文件，例如：
  ```yaml
  services:
    qbittorrent:
      image: linuxserver/qbittorrent
      # ... 其他配置 ...
      volumes:
        - /etc/hosts:/etc/hosts:ro  # 挂载hosts文件为只读
        - ./config:/config
        - ./downloads:/downloads
  ```
        无论使用 `host` 还是 `bridge` 网络模式，都需要手动挂载；宿主机更新后，容器内也会同步生效。

---

## 技术栈

### 前端 (Frontend)
- **核心框架**: Vue 3, Vite
- **语言**: TypeScript
- **UI框架**: Bootstrap 5
- **状态管理**: Pinia
- **样式预处理**: Sass

### 后端 (Backend)
- **核心框架**: FastAPI (Python 3.11+)
- **服务器**: Uvicorn
- **任务调度**: APScheduler
- **依赖库**: python-hosts, transmission-rpc, dnspython, passlib, croniter, aiohttp

### 部署与运维 (DevOps)
- **容器化**: Docker (支持 AMD64/ARM64 多架构)
- **CI/CD**: GitHub Actions
- **核心组件**: CloudflareSpeedTest (内置)

---

## 参考项目

- [CloudflareSpeedTest](https://github.com/XIU2/CloudflareSpeedTest) - 优质Cloudflare IP测速工具
- [GitHub Hosts](https://gitlab.com/ineo6/hosts) - 优质GitHub加速hosts源

---

## 版本更新日志

### 最新版本 (v2.2.3)

- ✅ **Hosts 源关闭即时生效**：关闭任意 Hosts 源后，后端会立即触发一次 Hosts 重建，并清理旧的合并备份，避免已关闭源继续参与优选。
- ✅ **通知推送结构优化**：统一优化 `IP优选与Hosts更新`、`仅更新Hosts`、`清空并更新Hosts` 的通知标题与内容排版，重点信息展示更清晰。
- ✅ **交互与资源加载改进**：Hosts 源开关增加前端状态提示与防重复点击保护，同时将 Boxicons 改为本地加载，减少外部 CDN 依赖。

### 版本历史

- **v2.2.3** (2026-04-15) - 优化 Hosts 源关闭后的即时重建流程、通知推送展示格式，并改为本地加载 Boxicons 资源
- **v2.2.1** (2026-03-29) - UI细节优化
- **v2.2.0** (2026-03-27) - UI 全面重构，优化视觉设计与交互体验
- **v2.1.0** (2026-02-26) - 修复批量更新IP确定按钮悬停样式、Trackers列表支持多字段点击排序、增强批量添加提示与稳定性
- **v2.0.8** (2026-01-01) - 修复一言API超时问题
- **v2.0.7** (2025-12-30) - 优化日志显示策略：前端日志极简模式，移动端通知保留详细信息
- **v2.0.6** (2025-12-30) - 修复定时任务僵死问题(Host/Notify超时保护)，优化Shell脚本非交互运行逻辑
- **v2.0.5** (2025-11-17) - 修复企业微信App加载渠道配置编辑失败问题，新增转发代理配置
- **v2.0.4** (2025-11-16) - 修复定时任务跳过执行问题、修复多通知渠道重复发送问题
- **v2.0.3** (2025-10-12) - 添加Media Saber通知渠道
- **v2.0.2** (2025-10-11) - 修复自定义通知配置问题
- **v2.0.1** (2025-10-11) - 修复自定义通知配置问题
- **v2.0.0** (2025-09-25) - 架构自适应支持、多通知渠道、移动端适配、Hosts结构保护
- **v1.0.0** (2025-04-29) - 初始版本发布

---

## 许可证

MIT License

---

如有问题、建议或需求，欢迎在GitHub Issue区反馈！
