/**
 * 认证 API
 * 后端路由: /api/auth/*
 */
import { authApi } from './axios';

export interface AuthStatus {
    logged_in?: boolean;
    is_authenticated?: boolean;
    username?: string;
    user?: {
        username: string;
    };
}

export interface LoginRequest {
    username: string;
    password: string;
}

export const auth = {
    // 登录 - 发送 JSON 格式
    login: (data: LoginRequest) =>
        authApi.post('/auth/login', data),

    // 登出
    logout: () =>
        authApi.post('/auth/logout', null, {
            headers: { 'Accept': 'application/json' }
        }),

    // 获取认证状态
    status: () =>
        authApi.get<AuthStatus>('/auth/status'),

    // 获取版本信息
    getVersion: () =>
        authApi.get<{ version: string }>('/auth/version'),
};
