/**
 * 小米路由器 Hosts API
 * 后端路由: /api/mihosts/*
 */
import api from './axios';

// ==================== 类型定义 ====================

export interface MiHostsConfig {
  enabled: boolean;
  app_id: string;
  device_id: string;
  client_id: string;
  scope: string;
  token?: string;
  ignore?: string;
}

export interface MiHostsStatus {
  enabled: boolean;
  app_id: string;
  device_id: string;
  client_id: string;
  scope: string;
  token: string;
  ignore: string;
}

export interface MiHostsRemoteHost {
  domain: string;
  ip: string;
  raw: string;
}

export interface MiHostsRemoteHostsResponse {
  success: boolean;
  message?: string;
  hosts: MiHostsRemoteHost[];
  raw_text: string;
  count: number;
}

export interface MiHostsSyncResult {
  success: boolean;
  message: string;
  cf_count?: number;
}

export interface MiHostsActionResult {
  success: boolean;
  message: string;
}

// ==================== API ====================

export const mihosts = {
  // 获取配置状态
  getStatus: () =>
    api.get<MiHostsStatus>('/mihosts/status'),

  // 测试连接
  test: (data?: Partial<MiHostsConfig>) =>
    api.post<MiHostsActionResult>('/mihosts/test', data || {}),

  // 获取远程 hosts 内容
  getRemoteHosts: () =>
    api.get<MiHostsRemoteHostsResponse>('/mihosts/remote-hosts'),

  // 同步 CFST 结果到小米路由器
  sync: () =>
    api.post<MiHostsSyncResult>('/mihosts/sync'),
};
