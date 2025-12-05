import { defineStore } from 'pinia';
import axios from '../api/axios';

export interface TorrentClient {
    id: string;
    name: string;
    type: string;
    host: string;
    port: number;
    username?: string;
    password?: string;
    use_https: boolean;
    path?: string;
    enable: boolean;
    version?: string;
}

export interface ClientType {
    type: string;
    name: string;
    default_port: number;
}

export const useClientStore = defineStore('clients', {
    state: () => ({
        clients: [] as TorrentClient[],
        supportedTypes: [] as ClientType[],
        loading: false,
    }),
    actions: {
        async fetchClients() {
            this.loading = true;
            try {
                const response = await axios.get('/torrent-clients');
                this.clients = response.data.clients || [];
            } finally {
                this.loading = false;
            }
        },
        async fetchSupportedTypes() {
            const response = await axios.get('/torrent-client-types');
            this.supportedTypes = response.data.types || [];
        },
        async saveClients(clients: TorrentClient[]) {
            await axios.post('/torrent-clients', { clients });
            this.clients = clients;
        },
        async deleteClient(id: string) {
            await axios.delete(`/torrent-clients/${id}`);
            // Remove from local state
            this.clients = this.clients.filter(c => c.id !== id);
        },
        async testConnection(clientId: string) {
            const response = await axios.post('/test-client-connection', { client_id: clientId });
            return response.data;
        },
        async testConnectionConfig(config: TorrentClient) {
            const response = await axios.post('/test-client-connection', { client_config: config });
            return response.data;
        },
        async importTrackers() {
            const response = await axios.post('/import-trackers-from-clients');
            return response.data;
        }
    },
});
