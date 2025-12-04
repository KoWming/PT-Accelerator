import { defineStore } from 'pinia';
import axios from '../api/axios';

export interface HostsSource {
    name: string;
    url: string;
    enable: boolean;
}

export const useHostsStore = defineStore('hosts', {
    state: () => ({
        sources: [] as HostsSource[],
        currentHosts: '',
        loading: false,
    }),
    actions: {
        async fetchConfig() {
            this.loading = true;
            try {
                const response = await axios.get('/config');
                this.sources = response.data.hosts_sources || [];
            } finally {
                this.loading = false;
            }
        },
        async fetchCurrentHosts() {
            const response = await axios.get('/current-hosts');
            if (Array.isArray(response.data.hosts)) {
                this.currentHosts = response.data.hosts.join('');
            } else {
                this.currentHosts = response.data.hosts || '';
            }
        },
        async addSource(source: HostsSource) {
            await axios.post('/hosts-sources', source);
            await this.fetchConfig();
        },
        async deleteSource(url: string) {
            await axios.delete(`/hosts-sources?url=${encodeURIComponent(url)}`);
            await this.fetchConfig();
        },
        async updateSource(url: string, data: Partial<HostsSource>) {
            // Similar to trackers, we need to update the full config or find a way.
            // We will fetch full config, update, and save.
            const response = await axios.get('/config');
            const fullConfig = response.data;
            const sources = fullConfig.hosts_sources || [];
            const idx = sources.findIndex((s: any) => s.url === url);
            if (idx !== -1) {
                sources[idx] = { ...sources[idx], ...data };
                fullConfig.hosts_sources = sources;
                await axios.post('/config', fullConfig);
                this.sources = sources;
            }
        },
        async updateHosts() {
            await axios.post('/update-hosts');
            await this.fetchCurrentHosts();
        },
        async clearAndUpdateHosts() {
            await axios.post('/clear-and-update-hosts');
            await this.fetchCurrentHosts();
        },
        async saveHostsContent(content: string) {
            await axios.post('/save-hosts-content', { content });
            this.currentHosts = content;
        }
    },
});
