import { defineStore } from 'pinia';
import { trackers, cfst } from '@/api';


const normalizeDomain = (value: string) => {
    const trimmed = (value || '').trim().toLowerCase();
    if (!trimmed) return '';
    try {
        if (trimmed.includes('://')) {
            return new URL(trimmed).hostname.toLowerCase();
        }
    } catch {
        // ignore parse error and fallback to manual extraction
    }
    return ((trimmed.replace(/^[a-z]+:\/\//, '').split('/')[0] ?? '').split(':')[0] ?? '').replace(/\.$/, '');
};

const getCloudflareDomainList = (payload: any): string[] => {
    const list = payload?.domains;
    if (!Array.isArray(list)) return [];
    return Array.from(new Set(
        list
            .map((item: unknown) => normalizeDomain(String(item || '')))
            .filter(Boolean)
    )).sort((a, b) => a.localeCompare(b));
};


export interface Tracker {
    id?: string;
    name: string;
    url: string;
    enabled: boolean;
    ip?: string;
}

export const useTrackerStore = defineStore('trackers', {
    state: () => ({
        trackers: [] as Tracker[],
        loading: false,
    }),
    actions: {
        async fetchTrackers() {
            this.loading = true;
            try {
                const response = await trackers.list();
                this.trackers = (response.data.trackers || []).map((t: any) => ({
                    id: t.id,
                    name: t.name,
                    url: t.url,
                    enabled: Boolean(t.enabled),
                    ip: t.ip,
                }));
            } finally {
                this.loading = false;
            }
        },

        async addTracker(tracker: Pick<Tracker, 'name' | 'url' | 'enabled'>, forceCloudflare: boolean = false) {
            const url = tracker.url || '';
            await trackers.create({
                name: tracker.name,
                url,
                enabled: tracker.enabled,
            });

            if (forceCloudflare) {
                const domain = normalizeDomain(url);
                if (domain) {
                    await this.includeCloudflareDomain(domain);
                    return;
                }
            }

            await this.fetchTrackers();
        },

        async updateTracker(trackerId: string | undefined, data: Partial<Pick<Tracker, 'name' | 'url' | 'enabled'>>) {
            if (!trackerId) return;
            const tracker = this.trackers.find((item) => item.id === trackerId);
            if (tracker) {
                await trackers.update(trackerId, {
                    name: data.name || tracker.name,
                    url: data.url || tracker.url,
                    enabled: data.enabled ?? tracker.enabled,
                });
            }
            await this.fetchTrackers();
        },

        async deleteTracker(trackerId: string | undefined) {
            if (!trackerId) return;
            await trackers.delete(trackerId);
            await this.fetchTrackers();
        },

        async deleteTrackers(trackerIds: string[]) {
            const deletedIds: string[] = [];
            const failedIds: string[] = [];
            // Serialize writes: the backend persists the complete Tracker list.
            for (const id of new Set(trackerIds)) {
                try {
                    await trackers.delete(id);
                    deletedIds.push(id);
                    this.trackers = this.trackers.filter(item => item.id !== id);
                } catch {
                    failedIds.push(id);
                }
            }
            return { deletedIds, failedIds };
        },

        async batchImport(urls: string[], enabled = true) {
            const response = await trackers.batchImport(urls, enabled);
            await this.fetchTrackers();
            return response.data;
        },

        async updateAllTrackersIp(ip: string) {
            const response = await trackers.batchUpdateIp(ip);
            await this.fetchTrackers();
            return response.data;
        },

        async clearAllTrackers() {
            const response = await trackers.clearAll();
            await this.fetchTrackers();
            return response.data;
        },

        async runIpOptimization() {
            return cfst.run();
        },

        async loadCloudflareDomains() {
            const response = await trackers.listCloudflareDomains();
            return getCloudflareDomainList(response.data);
        },

        async includeCloudflareDomain(domain: string | undefined) {
            return this.includeCloudflareDomains([domain || '']);
        },

        async includeCloudflareDomains(domains: string[]) {
            const normalized = domains.map(normalizeDomain).filter(Boolean);
            if (!normalized.length) return 0;
            const current = await this.loadCloudflareDomains();
            const merged = Array.from(new Set([...current, ...normalized]));
            await trackers.updateCloudflareDomains(merged);
            await this.fetchTrackers();
            return merged.length - current.length;
        },

        async excludeCloudflareDomain(domain: string | undefined) {
            const normalized = normalizeDomain(domain || '');
            if (!normalized) return;
            const current = await this.loadCloudflareDomains();
            await trackers.updateCloudflareDomains(current.filter(item => item !== normalized));
            await this.fetchTrackers();
        },
    },
});




