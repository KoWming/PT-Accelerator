import { defineStore } from 'pinia';
import axios from '../api/axios';

export interface Tracker {
    name: string;
    domain: string;
    enable: boolean;
    ip?: string;
}

export interface CloudflareConfig {
    enable: boolean;
    cron: string;
    ipv6?: boolean;
    additional_args?: string;
    notify?: boolean;
}

export const useTrackerStore = defineStore('trackers', {
    state: () => ({
        trackers: [] as Tracker[],
        cloudflare: {
            enable: true,
            cron: '0 0 * * *',
        } as CloudflareConfig,
        loading: false,
    }),
    actions: {
        async fetchConfig() {
            this.loading = true;
            try {
                const response = await axios.get('/config');
                const trackersData = response.data.trackers || [];
                // 确保 Vue3/Pinia 中的数组响应式触发
                this.trackers.splice(0, this.trackers.length, ...trackersData);
                this.cloudflare = response.data.cloudflare || {};
            } finally {
                this.loading = false;
            }
        },
        async addTracker(tracker: Tracker, forceCloudflare: boolean = false) {
            await axios.post(`/trackers?force_cloudflare=${forceCloudflare}`, tracker);
            await this.fetchConfig();
        },
        async deleteTracker(domain: string) {
            await axios.delete(`/trackers/${domain}`);
            await this.fetchConfig();
        },
        async updateTracker(domain: string, data: Partial<Tracker>) {
            // The backend doesn't have a specific update endpoint for a single tracker,
            // we update the whole config or find a way.
            // In main.js, updateTracker fetches config, modifies it, and posts back.
            // We should replicate that or improve backend.
            // For now, let's replicate the frontend logic: fetch, modify, save.
            // Wait, fetchConfig updates the state. We can modify state and save.

            const trackerIndex = this.trackers.findIndex(t => t.domain === domain);
            const item = this.trackers[trackerIndex];
            if (trackerIndex !== -1 && item) {
                // Optimistic update
                const oldTracker = { ...item };
                this.trackers[trackerIndex] = { ...oldTracker, ...data };

                try {
                    // We need to send the full config to /api/config
                    // But fetching full config first is safer to avoid overwriting other changes.
                    const response = await axios.get('/config');
                    const fullConfig = response.data;
                    const trackers = fullConfig.trackers || [];
                    const idx = trackers.findIndex((t: any) => t.domain === domain);
                    if (idx !== -1) {
                        trackers[idx] = { ...trackers[idx], ...data };
                        fullConfig.trackers = trackers;
                        await axios.post('/config', fullConfig);
                    }
                } catch (e) {
                    // Revert
                    this.trackers[trackerIndex] = oldTracker;
                    throw e;
                }
            }
        },
        async saveCloudflareConfig(config: CloudflareConfig) {
            const response = await axios.get('/config');
            const fullConfig = response.data;
            fullConfig.cloudflare = config;
            await axios.post('/config', fullConfig);
            this.cloudflare = config;
        },
        async batchAddTrackers(domains: string[]) {
            const response = await axios.post('/batch-add-domains', { domains });
            if (response.data && response.data.status === 'error') {
                throw new Error(response.data.message || '批量添加失败');
            }
            await this.fetchConfig();
            return response.data;
        },
        async updateAllTrackersIp(ip: string) {
            await axios.post(`/update-all-trackers?ip=${ip}`);
            await this.fetchConfig();
        },
        async clearAllTrackers() {
            await axios.post('/clear-all-trackers');
            await this.fetchConfig();
        },
        async runIpOptimization() {
            await axios.post('/run-cfst-script');
        },
        async fetchCloudflareDomains() {
            const response = await axios.get('/cloudflare-domains');
            return response.data.cloudflare_domains || [];
        },
        async addCloudflareDomain(domain: string) {
            await axios.post(`/cloudflare-domains?domain=${domain}`);
        },
        async deleteCloudflareDomain(domain: string) {
            await axios.delete(`/cloudflare-domains?domain=${domain}`);
        }
    },
});
