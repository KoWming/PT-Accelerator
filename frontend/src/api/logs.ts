/**
 * 日志 API
 * 后端路由: /api/logs (GET), /api/logs/clear (POST)
 */
import api from './axios';

// ==================== 类型定义 ====================

export interface LogQuery {
    lines?: number; // 返回最近 N 行日志，默认 1000，最大 10000
}

// ==================== 日志 API ====================

export const logs = {
    // 获取日志内容
    list: (params?: LogQuery) =>
        api.get<{ logs: string }>('/logs', { params }),

    // 清除日志
    clear: () =>
        api.post('/logs/clear'),
};
