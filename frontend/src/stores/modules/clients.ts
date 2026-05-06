import { defineStore } from 'pinia';
import { clients } from '@/api';

// 兼容旧属性名
export interface Downloader {
    id: string;
    name: string;
    type: string;
    host: string;
    port: number;
    username?: string;
    password?: string;
    enabled?: boolean;
    enable?: boolean;
    version?: string;
    path?: string;
}

export type TorrentClient = Downloader;

export interface ClientType {
    type: string;
    name: string;
    default_port: number;
}

export const useClientStore = defineStore('clients', {
    state: () => ({
        clients: [] as Downloader[],
        supportedTypes: [] as ClientType[],
        loading: false,
    }),
    getters: {
        getClientById: (state) => (id: string) => {
            return state.clients.find(c => c.id === id);
        },
    },
    actions: {
        // 获取下载器列表
        async fetchClients() {
            this.loading = true;
            try {
                const response = await clients.list();
                // host 字段现在直接包含完整地址（带协议和端口）
                this.clients = (response.data.downloaders || []).map((d: any) => {
                    return {
                        id: d.id,
                        name: d.name,
                        type: d.type,
                        host: d.host,
                        port: d.port,
                        username: d.username,
                        password: d.password,
                        enabled: d.enabled,
                        version: d.version,
                        // 兼容旧属性
                        enable: d.enabled,
                    };
                });
            } finally {
                this.loading = false;
            }
        },

        // 兼容旧方法
        async fetchConfig() {
            return this.fetchClients();
        },

        // 获取支持的客户端类型
        async fetchSupportedTypes() {
            const response = await clients.getTypes();
            const types = response.data?.types || [];
            this.supportedTypes = types.map((item: any) => ({
                type: item.type,
                name: item.name,
                default_port: item.default_port,
            }));
        },


        // 兼容旧方法
        async fetchClientTypes() {
            await this.fetchSupportedTypes();
        },

        // 添加下载器 - host 直接存储完整地址
        async addClient(data: Downloader) {
            const isEnabled = data.enable ?? data.enabled ?? true;

            // host 直接存储完整地址（可能包含协议）
            await clients.create({
                name: data.name,
                type: data.type as any,
                host: data.host,
                port: data.port,
                username: data.username,
                password: data.password,
                enabled: isEnabled,
                version: data.version,
            });
            await this.fetchClients();
        },

        // 更新下载器 - host 直接存储完整地址
        async updateClient(clientId: string, data: Downloader) {
            const isEnabled = data.enable ?? data.enabled ?? true;

            // host 直接存储完整地址（可能包含协议）
            await clients.update(clientId, {
                name: data.name,
                type: data.type as any,
                host: data.host,
                port: data.port,
                username: data.username,
                password: data.password,
                enabled: isEnabled,
                version: data.version,
            });
            await this.fetchClients();
        },

        // 删除下载器
        async deleteClient(clientId: string | undefined) {
            if (!clientId) return;
            await clients.delete(clientId);
            this.clients = this.clients.filter(c => c.id !== clientId);
        },

        // 兼容旧方法
        async deleteTorrentClient(id: string | undefined) {
            return this.deleteClient(id);
        },

        // 测试连接（已保存的客户端）
        async testConnection(clientId: string | undefined): Promise<any> {
            if (!clientId) return { success: false, message: '无效的客户端ID' };
            try {
                const result = await clients.test(clientId);
                return result.data;
            } catch (e: any) {
                return { success: false, message: e.message || '测试失败' };
            }
        },

        // 测试连接（临时配置）- host 直接包含完整地址
        async testConnectionConfig(config: Downloader) {
            const result = await clients.testByConfig({
                type: config.type as any,
                host: config.host,
                port: config.port,
                username: config.username,
                password: config.password,
            });
            return result.data;
        },

        // 兼容旧导入 trackers 方法
        async importTrackers() {
            const result = await clients.importTrackers();
            return result.data;
        },


        // 兼容旧保存方法
        async saveClients(_clients: Downloader[]) {
            // 需要逐个添加/更新
            console.warn('saveClients: 请使用 addClient/updateClient 方法');
        },
    },
});
