import { defineStore } from 'pinia';
import axios from '../api/axios';

export const useLogStore = defineStore('logs', {
    state: () => ({
        logs: '',
        loading: false,
    }),
    actions: {
        async fetchLogs(lines: number = 1000) {
            this.loading = true;
            try {
                const response = await axios.get(`/logs?lines=${lines}`);
                const data = response.data;
                if (typeof data.logs === 'string') {
                    this.logs = data.logs;
                } else if (Array.isArray(data.logs)) {
                    this.logs = data.logs.join('');
                } else {
                    this.logs = '';
                }
            } finally {
                this.loading = false;
            }
        },
        async clearLogs() {
            await axios.post('/logs/clear');
            this.logs = '';
        }
    },
});
