import { defineStore } from 'pinia';
import { auth, type LoginRequest } from '@/api';

interface AuthStatusResponse {
    logged_in?: boolean;
    is_authenticated?: boolean;
    username?: string;
    user?: { username: string };
    initialized?: boolean;
}

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null as { username: string } | null,
        isAuthenticated: false,
        initialized: false,
    }),
    actions: {
        async login(data: LoginRequest) {
            const response = await auth.login(data);
            const result = response.data;

            // 适配 ApiResponse 格式：{ success: true, data: {...} }
            if (result && (result.success !== false)) {
                this.isAuthenticated = true;
                await this.checkAuth();
            } else {
                throw new Error(result?.message || 'Login failed');
            }

            return response;
        },
        async logout() {
            await auth.logout();
            this.user = null;
            this.isAuthenticated = false;
        },
        async checkAuth() {
            try {
                const response = await auth.status();
                const rawData = response.data;

                // 适配后端返回格式：{ logged_in, username } 或 ApiResponse{ success, data: {...} }
                const statusData = (rawData as any)?.data || rawData as AuthStatusResponse;

                // 同时支持 logged_in 和 is_authenticated
                this.isAuthenticated = statusData?.logged_in || statusData?.is_authenticated || false;

                // 适配 user 字段
                if (statusData?.username) {
                    this.user = { username: statusData.username };
                } else if (statusData?.user) {
                    this.user = statusData.user;
                } else {
                    this.user = null;
                }

                this.initialized = statusData?.initialized ?? true;
            } catch (error) {
                this.isAuthenticated = false;
                this.user = null;
                this.initialized = false;
            }
        }
    },
});
