/**
 * 备份 API
 * 后端路由: /backup/*
 */
import api from './axios';

// ==================== 类型定义 ====================

export interface BackupInfo {
    id: string;
    file: string;
    size: number;
    created_at: string;
    source?: 'local' | 'remote';
}


export interface BackupConfig {
    webdav_enabled: boolean;
    webdav_url: string;
    webdav_username: string;
    webdav_password: string;
    webdav_path: string;
    local_keep_count: number;
}

export interface BackupTestPayload {
    webdav_url: string;
    webdav_username: string;
    webdav_password: string;
    webdav_path: string;
}

// ==================== 备份 API ====================

export const backup = {

    // 获取备份配置
    getConfig: () =>
        api.get<BackupConfig>('/backup/config'),

    // 更新备份配置
    updateConfig: (data: Partial<BackupConfig>) =>
        api.put('/backup/config', data),

    // 测试 WebDAV 连接（不保存配置）
    test: (data: BackupTestPayload) =>
        api.post('/backup/test', data),

    // 获取备份历史

    list: () =>
        api.get<{ backups: BackupInfo[]; total: number }>('/backup/history'),

    // 手动触发备份
    run: (description?: string) =>
        api.post('/backup/run', { description }),

    // 恢复备份
    restore: (backupId: string) =>
        api.post(`/backup/${backupId}/restore`),

    // 删除备份
    delete: (backupId: string) =>
        api.delete(`/backup/history/${backupId}`),

    // 上传已有备份到 WebDAV
    upload: (backupId: string) =>
        api.post(`/backup/${backupId}/upload`),

};
