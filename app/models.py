"""
Pydantic 数据模型（请求 / 响应 / 内部模型）
Phase 5：补充 request/response wrapper + Pipeline 状态模型
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


# ==================== 通用 ====================


class ApiResponse(BaseModel):
    """统一 API 响应格式"""
    success: bool = True
    data: Optional[Any] = None
    message: str = ""


class ErrorResponse(BaseModel):
    """统一错误响应"""
    success: bool = False
    message: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str


# ==================== Auth ====================


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    success: bool = True
    username: str
    message: str = ""


class PasswordChangeRequest(BaseModel):
    old_password: Optional[str] = None
    new_password: str = Field(min_length=1, max_length=128)



# ==================== CFST ====================


class CfstConfigIn(BaseModel):
    """CFST 参数配置（请求）"""
    threads: int = Field(default=200, ge=1, le=1000)
    ping_times: int = Field(default=4, ge=1, le=20)
    download_count: int = Field(default=20, ge=1, le=100)

    download_time: int = Field(default=10, ge=1, le=300)
    timeout_seconds: int = Field(default=300, ge=30, le=3600)
    tcp_port: int = Field(default=443, ge=1, le=65535)
    url: str = ""
    httping: bool = False
    httping_code: str = ""
    cfcolo: str = ""
    min_delay: int = Field(default=0, ge=0, le=9999)
    max_delay: int = Field(default=200, ge=0, le=9999)
    max_loss_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    min_speed: float = Field(default=0.0, ge=0.0)
    show_count: int = Field(default=10, ge=0, le=100)
    test_all: bool = False
    disable_download: bool = False
    debug: bool = False
    additional_args: str = ""


class CfstConfigOut(BaseModel):
    """CFST 参数配置（响应）"""
    threads: int
    ping_times: int
    download_count: int
    download_time: int
    timeout_seconds: int
    tcp_port: int
    url: str
    httping: bool
    httping_code: str
    cfcolo: str
    min_delay: int
    max_delay: int
    max_loss_rate: float
    min_speed: float
    show_count: int
    test_all: bool
    disable_download: bool
    debug: bool
    additional_args: str
    binary_path: Optional[str] = None



class CfstResultOut(BaseModel):
    """测速结果（单条）"""
    ip: str
    sent: Optional[int] = None
    received: Optional[int] = None
    loss_rate: Optional[float] = None
    avg_latency: Optional[float] = None
    download_speed: Optional[float] = None
    location: str = ""


class CfstResultsOut(BaseModel):
    """测速结果列表（响应）"""
    results: list[dict] = Field(default_factory=list)
    total: int = 0
    best_ip: Optional[str] = None
    result_file: Optional[str] = None


class CfstStatusOut(BaseModel):
    """测速状态（响应）"""
    running: bool
    progress: int = Field(ge=0, le=100)
    message: str = ""
    started_at: Optional[datetime] = None
    task_id: Optional[str] = None
    result_count: int = 0


class CfstRunIn(BaseModel):
    """手动触发测速（请求）"""
    pass


class CfstRunOut(BaseModel):
    """手动触发测速（响应）"""
    task_id: str
    message: str = "测速任务已提交"



# ==================== Hosts ====================


class HostsSourceIn(BaseModel):
    """Hosts 源配置（请求）"""
    name: str
    url: str
    enabled: bool = True


class HostsSourceOut(HostsSourceIn):
    id: str



class HostsSourceCreateOut(BaseModel):
    """创建 Hosts 源（响应）"""
    id: str
    message: str = "Hosts 源已创建"


class HostsSourceUpdateOut(BaseModel):
    message: str = "Hosts 源已更新"


class HostsSourceUpdateIn(BaseModel):
    """更新 Hosts 源（请求）"""
    name: Optional[str] = None
    url: Optional[str] = None
    enabled: Optional[bool] = None



class HostsSourceDeleteOut(BaseModel):
    message: str = "Hosts 源已删除"


class HostsSourceListOut(BaseModel):
    sources: list[dict]
    total: int


class HostsIpOut(BaseModel):
    """当前 Hosts 中的 CF IP"""
    tracker: str
    ip: str
    source: str
    updated_at: Optional[datetime] = None


class HostsIpListOut(BaseModel):
    ips: list[dict]
    total: int


class HostsUpdateIn(BaseModel):
    """手动更新 Hosts（请求）"""
    force: bool = Field(default=False, description="强制更新，忽略缓存")


class HostsUpdateOut(BaseModel):
    message: str = "Hosts 更新已提交"
    task_id: str


# ==================== Tracker ====================


class TrackerIn(BaseModel):
    """Tracker 配置（请求）"""
    name: str = Field(min_length=1)
    url: str = Field(min_length=1)
    enabled: bool = True


class TrackerOut(TrackerIn):
    """Tracker 配置（响应）"""
    id: str
    ip: Optional[str] = None




class TrackerCreateOut(BaseModel):

    id: str
    message: str = "Tracker 已创建"


class TrackerUpdateOut(BaseModel):
    message: str = "Tracker 已更新"


class TrackerDeleteOut(BaseModel):
    message: str = "Tracker 已删除"


class TrackerClearOut(BaseModel):
    cleared: int = 0
    message: str = "Tracker 已清空"


class TrackerBatchUpdateIpIn(BaseModel):
    ip: str = Field(min_length=1)


class TrackerBatchUpdateIpOut(BaseModel):
    updated: int = 0
    ip: str
    message: str = "Tracker IP 已批量更新"


class TrackerListOut(BaseModel):


    trackers: list[dict]
    total: int


class TrackerBatchImportIn(BaseModel):
    """批量导入 Tracker（请求）"""
    urls: list[str] = Field(min_length=1)
    enabled: bool = True


class TrackerBatchImportOut(BaseModel):
    imported: int
    skipped: int
    cloudflare_domains: list[str] = Field(default_factory=list)
    non_cloudflare_domains: list[str] = Field(default_factory=list)
    torrent_count: int = 0
    tracker_count: int = 0
    unique_tracker_count: int = 0
    client_summary: str = ""
    message: str = "批量导入完成"


class TrackerImportTaskOut(BaseModel):
    task_id: str
    message: str = "Tracker 导入后台任务已启动"


class TrackerCloudflareDomainsIn(BaseModel):
    domains: list[str] = Field(default_factory=list)


class TrackerCloudflareDomainsOut(BaseModel):
    domains: list[str] = Field(default_factory=list)
    total: int = 0

# ==================== Downloader ====================



class DownloaderIn(BaseModel):
    """下载器配置（请求）"""
    name: str = Field(min_length=1, description="客户端名称")
    type: str = Field(description="qbittorrent | transmission")
    host: str
    port: int = Field(ge=1, le=65535)
    username: str = ""
    password: str = ""
    enabled: bool = True
    version: Optional[str] = None  # 可选，用于保存下载器版本


class DownloaderOut(BaseModel):
    """下载器配置（响应）"""
    id: str
    name: str
    type: str
    host: str
    port: int
    username: str = ""
    enabled: bool


class DownloaderListOut(BaseModel):
    downloaders: list[dict]
    total: int


class DownloaderAddOut(BaseModel):
    id: str
    message: str = "下载器已添加"


class DownloaderDeleteOut(BaseModel):
    message: str = "下载器已删除"


class DownloaderTestIn(BaseModel):
    """测试下载器连接（请求）"""
    type: str
    host: str
    port: int
    username: str
    password: str


# ==================== Backup ====================


class BackupConfigIn(BaseModel):
    """备份配置（请求）"""
    webdav_enabled: bool = False
    webdav_url: str = ""
    webdav_username: str = ""
    webdav_password: str = ""
    webdav_path: str = "/backups"
    local_keep_count: int = Field(default=7, ge=1, le=30)


class BackupConfigOut(BaseModel):
    """备份配置（响应）"""
    webdav_enabled: bool
    webdav_url: str
    webdav_username: str
    webdav_password: str = ""  # 不返回明文密码
    webdav_path: str
    local_keep_count: int


class BackupCreateIn(BaseModel):
    """创建备份（请求）"""
    description: str = ""


class BackupCreateOut(BaseModel):
    backup_id: str
    message: str = "备份任务已提交"


class BackupListOut(BaseModel):
    backups: list[dict]
    total: int


class BackupRestoreIn(BaseModel):
    """恢复备份（请求）"""
    backup_id: str


class BackupRestoreOut(BaseModel):
    message: str = "恢复任务已提交"


class BackupDeleteOut(BaseModel):
    message: str = "备份已删除"


class BackupTestIn(BaseModel):
    """测试 WebDAV 连接（请求）"""
    webdav_url: str = ""
    webdav_username: str = ""
    webdav_password: str = ""
    webdav_path: str = "/backups"


class BackupTestOut(BaseModel):
    success: bool = True
    message: str = "WebDAV 连接测试成功"


# ==================== Notify ====================



class NotifyChannelIn(BaseModel):
    """通知渠道配置（请求）"""
    name: str = Field(min_length=1, description="渠道名称")
    type: str = Field(description="wecom_bot | wecom_app | telegram | igot | dingding | feishu | smtp | bark | serverj | chat | mediasaber | slack | webhook（兼容别名：wecom -> wecom_bot, dingtalk -> dingding）")
    enabled: bool = True
    config: dict = Field(default_factory=dict)


class NotifyChannelOut(NotifyChannelIn):
    """通知渠道配置（响应）"""
    id: str


class NotifyChannelCreateOut(BaseModel):
    id: str
    message: str = "通知渠道已创建"


class NotifyChannelUpdateOut(BaseModel):
    message: str = "通知渠道已更新"


class NotifyChannelDeleteOut(BaseModel):
    message: str = "通知渠道已删除"


class NotifyChannelListOut(BaseModel):
    channels: list[dict]
    total: int


class NotifyTestIn(BaseModel):
    """测试通知（请求）"""
    channel_id: str


class NotifyTestOut(BaseModel):
    message: str = "测试消息已发送"


# ==================== Pipeline 状态 ====================


class PipelineStatusOut(BaseModel):
    """任务管线状态（响应）"""
    pipeline_id: str
    name: str
    status: str = Field(description="idle | running | success | failed")
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    message: str = ""


# ==================== Scheduler ====================


class SchedulerJobIn(BaseModel):
    """调度任务配置（请求）"""
    job_id: str = Field(description="任务ID：cfst | hosts | backup")
    name: str = Field(min_length=1, description="任务名称")
    trigger: str = Field(description="触发类型：interval | cron")
    enabled: bool = True
    interval_seconds: Optional[int] = Field(default=3600, ge=60, le=604800, description="间隔秒数(interval)")
    cron_expr: Optional[str] = Field(default=None, description="Cron表达式( cron)，格式：分 时 日 月 周")


class SchedulerJobOut(SchedulerJobIn):
    """调度任务配置（响应）"""
    next_run: Optional[str] = None  # ISO 时间字符串
    last_run: Optional[str] = None
    status: str = Field(default="idle", description="idle | running | success | failed")


class SchedulerJobListOut(BaseModel):
    """调度任务列表（响应）"""
    jobs: list[dict]
    total: int
