/**
 * Hosts API
 * 后端路由: /hosts/*
 */
import api from './axios';

// ==================== 类型定义 ====================

export interface HostsSource {
    id: string;
    name: string;
    url: string;
    enabled: boolean;
    last_error?: string;
}


export interface HostsSourceIn {
    name: string;
    url: string;
    enabled: boolean;
}

export interface HostsSourceUpdateIn {
    name?: string;
    url?: string;
    enabled?: boolean;
}

// ==================== Hosts 源 CRUD ====================

export const hosts = {
    // 列出所有 Hosts 源
    listSources: () =>
        api.get<{ sources: HostsSource[]; total: number }>('/hosts/sources'),

    // 获取单个 Hosts 源
    getSource: (sourceId: string) =>
        api.get<HostsSource>(`/hosts/sources/${sourceId}`),

    // 新增 Hosts 源
    addSource: (data: HostsSourceIn) =>
        api.post('/hosts/sources', data),

    // 更新 Hosts 源
    updateSource: (sourceId: string, data: HostsSourceUpdateIn) =>
        api.put(`/hosts/sources/${sourceId}`, data),

    // 删除 Hosts 源
    deleteSource: (sourceId: string) =>
        api.delete(`/hosts/sources/${sourceId}`),

    // ==================== IP 映射 & 内容 ====================

    // 获取 tracker IP 映射
    getTrackerIps: () =>
        api.get<{ ips: Record<string, string>; total: number }>('/hosts/ips'),

    // 获取当前 Hosts 文件内容
    getContent: () =>
        api.get<{ content: string }>('/hosts/content'),

    // 保存 Hosts 文件内容
    saveContent: (content: string) =>
        api.put('/hosts/content', null, { params: { content } }),

    // ==================== 手动刷新 ====================

    // 手动刷新 Hosts（基于当前源和 CFST 结果直接合并写入）
    refresh: (force = false) =>
        api.post('/hosts/refresh', null, { params: { force } }),

    // 手动重建 Hosts（先清空项目分区再生成）
    rebuild: (force = true) =>
        api.post('/hosts/rebuild', null, { params: { force } }),



    // ==================== Hosts 配置 ====================

    // 获取 Hosts 配置
    getConfig: () =>
        api.get<{
            target_path: string;
            backup_enabled: boolean;
        }>('/hosts/config'),

    // 更新 Hosts 配置
    updateConfig: (targetPath?: string, backupEnabled?: boolean) =>
        api.put('/hosts/config', null, {
            params: { target_path: targetPath, backup_enabled: backupEnabled }
        }),
};
