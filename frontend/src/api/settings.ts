/**
 * 设置 API
 * 后端路由: /settings/*
 */
import api from './axios';

// ==================== 类型定义 ====================

export interface SystemInfo {
    version: string;
    uptime: string;
    uptime_seconds: number;
    platform: string;
    initialized: boolean;
    config_version?: string;
}

// ==================== 设置 API ====================

export const settings = {
    // 获取系统信息
    info: () =>
        api.get<SystemInfo>('/settings/info'),

    // 获取完整配置（密码脱敏）
    config: () =>
        api.get('/settings/config'),

    // 批量更新配置
    updateConfig: (data: Record<string, any>) =>
        api.put('/settings/config', data),

    // 修改密码
    changePassword: (newPassword: string, oldPassword?: string) =>
        api.put('/settings/password', {
            old_password: oldPassword || null,
            new_password: newPassword,
        }),

};
