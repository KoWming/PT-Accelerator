/**
 * 通知 API
 * 后端路由: /api/notify/*
 */
import api from './axios';

export interface NotifyChannelConfig {
    id: string;
    type: string;
    name: string;
    enabled: boolean;
    config: Record<string, any>;
}

export interface NotifyChannelIn {
    type: string;
    name: string;
    enabled: boolean;
    config: Record<string, any>;
}

export interface NotifyChannelTypeMeta {
    type: string;
    name: string;
    fields: string[];
}

export const notify = {
    listChannels: () =>
        api.get<{ channels: NotifyChannelConfig[]; total: number }>('/notify/'),

    getTypes: () =>
        api.get<{ types: NotifyChannelTypeMeta[] }>('/notify/types'),

    getChannel: (channelId: string) =>
        api.get<NotifyChannelConfig>(`/notify/${channelId}`),

    createChannel: (data: NotifyChannelIn) =>
        api.post('/notify/', data),

    updateChannel: (channelId: string, data: NotifyChannelIn) =>
        api.put(`/notify/${channelId}`, data),

    deleteChannel: (channelId: string) =>
        api.delete(`/notify/${channelId}`),

    testChannel: (channelId: string) =>
        api.post(`/notify/${channelId}/test`),
};

