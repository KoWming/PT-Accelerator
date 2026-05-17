"""
FastAPI 应用入口

注意：日志和配置初始化已在根目录 main.py 中完成，此处不再重复。

职责：
  1. 创建 FastAPI 实例
  2. 注册路由
  3. 配置 CORS
  4. 挂载静态文件（SPA）
  5. 启动时检测 CFST 二进制
  6. 启停调度器

启动方式：
  python main.py        # 从项目根目录启动（唯一入口）
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.staticfiles import StaticFiles

# CORS 来源白名单（本地 SPA + Docker 端口映射场景）
# 生产部署时，如有自定义域名，请将其追加到此列表
_CORS_ALLOW_ORIGINS = [
    "http://localhost:23333",
    "http://127.0.0.1:23333",
    "http://0.0.0.0:23333",
]
# 若环境变量 CORS_ORIGINS 提供了额外来源（逗号分隔），则合并
_extra_origins = os.environ.get("CORS_ORIGINS", "")
if _extra_origins:
    _CORS_ALLOW_ORIGINS.extend(
        o.strip() for o in _extra_origins.split(",") if o.strip()
    )

# 引用配置（已在 main.py 初始化）
from app.config import config
from app.services import scheduler_service
from app.utils.cfst_installer import CfstInstaller
from app.utils.logger import get_logger
from version import get_version

logger = get_logger(__name__)
APP_VERSION = get_version()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    installer = CfstInstaller()
    binary_path = installer.get_binary_path()

    if os.path.exists(binary_path):
        logger.info(f"启动检测通过：CFST 二进制已存在：{binary_path}")
    else:
        logger.warning("启动检测 CFST 二进制:")
        if installer.ensure():

            logger.info(f"启动阶段已完成 CFST 安装：{installer.get_binary_path()}")
        else:
            logger.error("启动阶段 CFST 自动安装失败，请按日志中的下载链接手动下载安装")

    scheduler_service.start_scheduler()

    try:
        yield
    finally:
        scheduler_service.shutdown_scheduler()


# 创建 FastAPI 实例
# OpenAPI 文档默认关闭（生产安全）
# 开启方式：config.yaml 中 app.debug: true，或环境变量 ENABLE_OPENAPI_DOCS=true
_debug = config.get("app.debug", False)
_enable_docs = _debug or os.environ.get("ENABLE_OPENAPI_DOCS", "false").lower() == "true"
_CSP_POLICY = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https:; "
    "font-src 'self' data:; "
    "connect-src 'self' https://v1.hitokoto.cn; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self'"
)

app = FastAPI(
    title="PT-Accelerator",
    version=config.get("app.version", APP_VERSION),
    debug=_debug,
    lifespan=lifespan,
    docs_url="/docs" if _enable_docs else None,
    redoc_url="/redoc" if _enable_docs else None,
    openapi_url="/openapi.json" if _enable_docs else None,
)


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = _CSP_POLICY
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
    return response

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ALLOW_ORIGINS,   # ✅ 明确白名单，禁止通配符
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-CSRF-Token"],
)

# 注册 API 路由（必须在 SPA catch-all 之前）
from app.routes import router as api_router
app.include_router(api_router, prefix="/api")


# ==================== 健康检查 ====================
@app.get("/api/health")
async def health_check():
    """健康检查（Docker healthcheck 使用）"""
    return {"status": "ok", "version": config.get("app.version")}


# 挂载 SPA 静态文件（优先使用 frontend/dist，其次兼容根目录 dist）
frontend_dist_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
legacy_dist_path = os.path.join(os.path.dirname(__file__), "..", "dist")
dist_path = frontend_dist_path if os.path.isdir(frontend_dist_path) else legacy_dist_path
if os.path.isdir(dist_path):
    # 1. 挂载 /static 路径的静态资源（如果有）
    dist_dir = Path(dist_path)
    assets_dir = dist_dir / "assets"

    # 1. 挂载 Vite 构建产物静态资源
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    # 2. 根目录静态文件（如 vite.svg、favicon 等）
    @app.get("/{file_path:path}")
    async def spa_fallback(file_path: str):
        """SPA fallback: 优先返回真实静态文件，排除 API 路由，其余交给前端路由。"""
        if file_path.startswith("api/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        requested_path = (dist_dir / file_path).resolve()
        try:
            requested_path.relative_to(dist_dir.resolve())
        except ValueError:
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        if file_path and requested_path.is_file():
            return FileResponse(str(requested_path))

        return FileResponse(str(dist_dir / "index.html"))


