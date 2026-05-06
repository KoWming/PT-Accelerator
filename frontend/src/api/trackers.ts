/**
 * Trackers API
 * 后端路由: /trackers/*
 */
import api from './axios';

// ==================== 类型定义 ====================

export interface Tracker {
    id: string;
    name: string;
    url: string;
    enabled: boolean;
    ip?: string;
}




export interface TrackerIn {
    name: string;
    url: string;
    enabled: boolean;
}

// ==================== Trackers API ====================

export const trackers = {
    // 列出所有 tracker
    list: () =>
        api.get<{ trackers: Tracker[]; total: number }>('/trackers/'),

    // 仅列出已启用的 tracker
    listEnabled: () =>
        api.get<{ trackers: Tracker[]; total: number }>('/trackers/enabled'),

    // 获取 Cloudflare 域名名单
    listCloudflareDomains: () =>
        api.get<{ domains: string[]; total: number }>('/trackers/cloudflare-domains'),

    // 更新 Cloudflare 域名名单
    updateCloudflareDomains: (domains: string[]) =>
        api.put('/trackers/cloudflare-domains', { domains }),

    // 获取单个 tracker
    get: (trackerId: string) =>
        api.get<Tracker>(`/trackers/${trackerId}`),

    // 新增 tracker
    create: (data: TrackerIn) =>
        api.post('/trackers/', data),

    // 更新 tracker
    update: (trackerId: string, data: TrackerIn) =>
        api.put(`/trackers/${trackerId}`, data),

    // 删除 tracker
    delete: (trackerId: string) =>
        api.delete(`/trackers/${trackerId}`),

    // 清空全部 tracker
    clearAll: () =>
        api.delete('/trackers/'),

    // 批量更新全部 tracker 的当前 IP
    batchUpdateIp: (ip: string) =>
        api.put('/trackers/ip', { ip }),

    // 批量导入 tracker


    batchImport: (urls: string[], enabled = true) =>
        api.post('/trackers/batch', { urls, enabled }),
};
