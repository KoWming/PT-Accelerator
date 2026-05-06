/**
 * 爱快 DNS API
 * 后端路由: /ikuai/*
 */
import api from './axios';

// ==================== 类型定义 ====================

export interface IkuaiConfig {
    enabled: boolean;
    host: string;
    username: string;
    password?: string;
}

export interface IkuaiStatus {
    enabled: boolean;
    host: string;
    username: string;
}

export interface IkuaiDnsRecord {
    id: string | number;
    domain: string;
    dns_addr: string;
    /** 解析类型，通常为 IPv4 / IPv6 */
    type?: string;
    /** 作用 IP 段 */
    src_addr?: string;
    /** 备注 */
    comment?: string;
    /** "yes"=启用 "no"=停用（爱快字段，部分旧固件也可能返回 1/0） */
    enabled?: number | string;
    [key: string]: any;
}

export interface IkuaiSyncNowResult {
    success: boolean;
    message: string;
    synced_count?: number;
    records?: Array<{ domain: string; ip: string }>;
}

export interface IkuaiActionResult {
    success: boolean;
    message: string;
}

// ==================== 爱快 DNS API ====================

export const ikuai = {
    // 获取状态/当前配置摘要
    getStatus: () =>
        api.get<IkuaiStatus>('/ikuai/status'),

    // 保存配置
    saveConfig: (data: Partial<IkuaiConfig>) =>
        api.post('/ikuai/save', data),

    // 获取同步记录
    getRecords: () =>
        api.get<{ success: boolean; records: IkuaiDnsRecord[] }>('/ikuai/records'),

    // 同步 DNS（需传入 hosts 列表）
    sync: (hosts: Array<{ domain: string; ip: string }>) =>
        api.post('/ikuai/sync', hosts),

    // 手动立即同步（复用 CFST 缓存结果，无需重跑优选）
    syncNow: () =>
        api.post<IkuaiSyncNowResult>('/ikuai/sync-now'),

    // 测试连接
    test: (data?: Partial<IkuaiConfig>) =>
        api.post('/ikuai/test', data || {}),

    // 导出 DNS 配置为 TXT（返回 Blob）
    exportDns: () =>
        api.post('/ikuai/export-dns', {}, { responseType: 'blob' }),

    // 导入 DNS 配置（content 为 Base64 字符串，append=true 时追加而非覆盖）
    importDns: (content: string, append: boolean = false) =>
        api.post<IkuaiActionResult>('/ikuai/import-dns', { content, append }),

    // 启用/停用 DNS 记录
    toggleRecord: (id: string | number, enable: boolean) =>
        api.post<IkuaiActionResult>('/ikuai/toggle-record', { id: String(id), enable }),

    // 删除 DNS 记录
    deleteRecord: (id: string | number) =>
        api.post<IkuaiActionResult>('/ikuai/delete-record', { id: String(id) }),
};


