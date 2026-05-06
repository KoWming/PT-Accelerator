export interface AuthFormState {
  username: string;
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface BackupFormState {
  enable: boolean;
  webdav_url: string;
  webdav_path: string;
  webdav_username: string;
  webdav_password: string;
  cron: string;
  backup_count: number;
}

export interface BackupItem {
  id: string;
  file: string;
  filename?: string;
  source?: 'local' | 'remote' | string;
  created_at: string;
  size: number;
}

export interface BackupGroupedItem {
  key: string;
  file: string;
  created_at: string;
  total_size: number;
  items: BackupItem[];
}


export interface CfstFormState {
  threads: number | null;
  ping_times: number | null;
  download_count: number | null;
  download_time: number | null;
  timeout_seconds: number | null;
  tcp_port: number | null;
  url: string;
  httping: boolean;
  httping_code: string;
  cfcolo: string;
  min_delay: number | null;
  max_delay: number | null;
  max_loss_rate: number | null;
  min_speed: number | null;
  show_count: number | null;
  test_all: boolean;
  disable_download: boolean;
  debug: boolean;
  additional_args: string;
}

export interface IkuaiDnsFormState {
  enable: boolean;
  url: string;
  username: string;
  password: string;
}

export interface MiHostsFormState {
  enable: boolean;
  app_id: string;
  device_id: string;
  client_id: string;
  scope: string;
  token: string;
  ignore: string;
}

export interface NotifyChannelPayload {
  name: string;
  type: string;
  enabled: boolean;
  config: Record<string, unknown>;
}

export interface NotifyChannel extends Record<string, unknown> {
  id: string;
  name: string;
  type: string;
  enabled: boolean;
  config?: Record<string, unknown>;
  HITOKOTO?: boolean;
}

export type SettingPageKey = 'system' | 'notification' | 'backup' | 'cfst' | 'ikuai-dns';

export interface PageFeedback {
  title: string;
  message: string;
  status: 'success' | 'error';
}

export interface SettingPageMeta {
  title: string;
  description: string;
}

export interface PageOverviewCard {
  label: string;
  value: string;
  description: string;
}


export interface CfstStatusState {
  running: boolean;
  task_id: string | null;
  progress: number;
  result_count: number;
  message: string;
  started_at: string | null;
}

export interface CfstResultItem {
  ip?: string;
  sent?: number;
  received?: number;
  loss_rate?: number | string;
  avg_latency?: number | string;
  download_speed?: number | string;
  location?: string;
  error?: string;
}
