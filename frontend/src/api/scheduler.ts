/**
 * 调度器 API
 * 后端路由: /scheduler/*
 */
import api from './axios';

// ==================== 类型定义 ====================

export type SchedulerTrigger = 'interval' | 'cron';
export type SchedulerJobStatus = 'idle' | 'scheduled' | 'running' | 'success' | 'failed';

export interface SchedulerJob {
    job_id: string;
    name: string;
    trigger: SchedulerTrigger;
    enabled: boolean;
    interval_seconds?: number;
    cron_expr?: string;
    next_run?: string | null;
    last_run?: string | null;
    status: SchedulerJobStatus;
}

export interface SchedulerJobIn {
    job_id: string;
    name: string;
    trigger: SchedulerTrigger;
    enabled: boolean;
    interval_seconds?: number;
    cron_expr?: string;
}

// ==================== 调度器 API ====================

export const scheduler = {
    // 获取调度器状态
    status: () =>
        api.get<{ running: boolean; jobs: SchedulerJob[] }>('/scheduler/status'),

    // 获取任务列表
    listJobs: () =>
        api.get<{ jobs: SchedulerJob[]; total: number }>('/scheduler/jobs'),

    // 获取单个任务
    getJob: (jobId: string) =>
        api.get<SchedulerJob>(`/scheduler/jobs/${jobId}`),

    // 创建/更新任务
    createJob: (data: SchedulerJobIn) =>
        api.post('/scheduler/jobs', data),

    // 删除任务
    deleteJob: (jobId: string) =>
        api.delete(`/scheduler/jobs/${jobId}`),

    // 启用任务
    enableJob: (jobId: string) =>
        api.post(`/scheduler/jobs/${jobId}/enable`),

    // 禁用任务
    disableJob: (jobId: string) =>
        api.post(`/scheduler/jobs/${jobId}/disable`),

    // 手动触发任务
    runJob: (jobId: string) =>
        api.post(`/scheduler/jobs/${jobId}/run`),
};
