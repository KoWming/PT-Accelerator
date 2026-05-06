/**
 * CFST API
 * 后端路由: /cfst/*
 */
import api from './axios';

export interface CfstConfig {
    threads: number;
    ping_times: number;
    download_count: number;
    download_time: number;
    tcp_port: number;
    url: string;
    httping: boolean;
    httping_code: string;
    cfcolo: string;
    min_delay: number;
    max_delay: number;
    max_loss_rate: number;
    min_speed: number;
    show_count: number;
    test_all: boolean;
    disable_download: boolean;
    debug: boolean;
    additional_args: string;
    binary_path?: string | null;
}

export interface CfstStatus {
    running: boolean;
    task_id: string | null;
    progress: number;
    result_count: number;
    message: string;
    started_at?: string | null;
}

export interface CfstResult {
    ip: string;
    sent?: number | null;
    received?: number | null;
    loss_rate?: number | null;
    avg_latency?: number | null;
    download_speed?: number | null;
    location?: string;
    timestamp?: string;
    error?: string;
}

export interface CfstRunOut {
    task_id: string;
    message: string;
}

export interface CfstResultsOut {
    results: CfstResult[];
    total: number;
    best_ip: string | null;
    result_file?: string | null;
}

export const cfst = {
    run: () => api.post<CfstRunOut>('/cfst/run', {}),
    getStatus: () => api.get<CfstStatus>('/cfst/status'),
    getResults: () => api.get<CfstResultsOut>('/cfst/results'),
    getConfig: () => api.get<CfstConfig>('/cfst/config'),
    updateConfig: (data: Partial<CfstConfig>) => api.put('/cfst/config', data),
};

