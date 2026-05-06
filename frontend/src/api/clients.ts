/**
 * 下载器 API
 * 后端路由: /clients/*
 */
import api from './axios';

// ==================== 类型定义 ====================

export type DownloaderType = 'qbittorrent' | 'transmission';

export interface Downloader {
    id: string;
    name: string;
    type: DownloaderType;
    host: string;
    port: number;
    username?: string;
    enabled: boolean;
    version?: string;
}

export interface DownloaderIn {
    name: string;
    type: DownloaderType;
    host: string;
    port: number;
    username?: string;
    password?: string;
    enabled?: boolean;
    version?: string;
}

export interface DownloaderTestIn {
    type: DownloaderType;
    host: string;
    port: number;
    username?: string;
    password?: string;
}

export interface ImportTrackersResult {
    imported: number;
    skipped: number;
    cloudflare_domains: string[];
    non_cloudflare_domains: string[];
    torrent_count: number;
    tracker_count: number;
    unique_tracker_count: number;
    client_summary: string;
    message: string;
}

export interface ImportTrackersTaskResult {
    task_id: string;
    message: string;
}

// ==================== 下载器 API ====================

export const clients = {
    // 列出所有下载器
    list: () =>
        api.get<{ downloaders: Downloader[]; total: number }>('/clients/'),

    // 获取支持的客户端类型
    getTypes: () =>
        api.get<{ types: string[] }>('/clients/types'),

    // 获取单个下载器
    get: (clientId: string) =>
        api.get<Downloader>(`/clients/${clientId}`),

    // 添加下载器
    create: (data: DownloaderIn) =>
        api.post('/clients/', data),

    // 更新下载器
    update: (clientId: string, data: DownloaderIn) =>
        api.put(`/clients/${clientId}`, data),

    // 删除下载器
    delete: (clientId: string) =>
        api.delete(`/clients/${clientId}`),

    // 测试下载器连接（已保存的客户端）
    test: (clientId: string) =>
        api.post(`/clients/${clientId}/test`),

    // 测试下载器连接（临时配置）
    testByConfig: (data: DownloaderTestIn) =>
        api.post('/clients/test', data),

    // 从已启用下载器导入 Tracker
    importTrackers: () =>
        api.post<ImportTrackersTaskResult>('/clients/import-trackers'),
};

export const clientsApi = clients;

export default clients;

