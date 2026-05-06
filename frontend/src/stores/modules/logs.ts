import { defineStore } from 'pinia';
import { logs } from '@/api';

export const useLogStore = defineStore('logs', {
    state: () => ({
        // 后端返回纯文本日志字符串
        logText: '' as string,
        loading: false,
    }),
    actions: {
        async fetchLogs(params?: { lines?: number }) {
            this.loading = true;
            try {
                const response = await logs.list(params);
                this.logText = response.data.logs || '';
            } finally {
                this.loading = false;
            }
        },

        async clearLogs() {
            await logs.clear();
            this.logText = '';
        },
    },
});
