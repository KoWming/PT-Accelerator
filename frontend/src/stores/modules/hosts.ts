import { defineStore } from 'pinia';
import { hosts } from '@/api';

export interface HostsSource {
    id?: string;
    name: string;
    url: string;
    enabled: boolean;
    last_error?: string;
}

export const useHostsStore = defineStore('hosts', {
    state: () => ({
        sources: [] as HostsSource[],
        currentHosts: '',
        currentHostsPath: '',
        isDevHosts: false,
        backupEnabled: true,
        loading: false,
    }),
    actions: {
        async fetchSources() {
            this.loading = true;
            try {
                const response = await hosts.listSources();
                this.sources = (response.data.sources || []).map((s: any) => ({
                    id: s.id,
                    name: s.name,
                    url: s.url,
                    enabled: Boolean(s.enabled),
                    last_error: s.last_error,
                }));
            } finally {
                this.loading = false;
            }
        },

        async fetchContent() {
            const [contentResponse, configResponse] = await Promise.all([
                hosts.getContent(),
                hosts.getConfig().catch(() => null),
            ]);

            this.currentHosts = contentResponse.data.content || '';

            const targetPath = String(configResponse?.data?.target_path || '').trim();
            this.currentHostsPath = targetPath;
            this.backupEnabled = Boolean(configResponse?.data?.backup_enabled ?? true);

            const normalizedPath = targetPath.replace(/\\/g, '/').toLowerCase();
            this.isDevHosts = normalizedPath.endsWith('/hosts.dev') || normalizedPath.endsWith('hosts.dev');
        },

        async fetchIps() {
            return hosts.getTrackerIps();
        },

        async addSource(source: Pick<HostsSource, 'name' | 'url' | 'enabled'>) {
            await hosts.addSource({
                name: source.name,
                url: source.url,
                enabled: source.enabled,
            });
            await this.fetchSources();
        },

        async updateSource(sourceId: string, data: Partial<Pick<HostsSource, 'name' | 'url' | 'enabled'>>) {
            await hosts.updateSource(sourceId, {
                name: data.name,
                url: data.url,
                enabled: data.enabled,
            });
            await this.fetchSources();
        },

        async deleteSource(sourceId: string) {
            await hosts.deleteSource(sourceId);
            await this.fetchSources();
        },

        async refreshHosts(force = false) {
            return hosts.refresh(force);
        },

        async rebuildHosts(force = true) {
            return hosts.rebuild(force);
        },

        async fetchHostsConfig() {
            return hosts.getConfig();
        },

        async updateConfig(targetPath?: string, backupEnabled?: boolean) {
            await hosts.updateConfig(targetPath, backupEnabled);
            await this.fetchContent();
        },

        async saveContent(content: string) {
            await hosts.saveContent(content);
            await this.fetchContent();
        },

        async saveHostsContent(content: string) {
            await this.saveContent(content);
        },
    },
});

