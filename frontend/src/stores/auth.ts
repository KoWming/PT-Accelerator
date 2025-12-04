import { defineStore } from 'pinia';
import axios from '../api/axios';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null as any | null,
        isAuthenticated: false,
    }),
    actions: {
        async login(formData: FormData) {
            // The backend expects form data for login
            // Override baseURL because login is at root, not /api
            const response = await axios.post('/login', formData, {
                baseURL: '/',
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Accept': 'application/json'
                }
            });

            // Backend returns JSON with success: true on success
            // On failure it returns 400, which axios throws as error

            if (response.data && response.data.success) {
                this.isAuthenticated = true;
                // Fetch user info after login
                await this.checkAuth();
            } else {
                throw new Error(response.data?.message || 'Login failed');
            }

            return response;
        },
        async logout() {
            // Override baseURL because logout is at root
            await axios.get('/logout', {
                baseURL: '/',
                headers: { 'Accept': 'application/json' }
            });
            this.user = null;
            this.isAuthenticated = false;
        },
        async checkAuth() {
            try {
                // axios instance has baseURL='/api', so this becomes /api/auth/status
                const response = await axios.get('/auth/status');
                const data = response.data;
                this.isAuthenticated = data.is_authenticated;
                this.user = data.user;
            } catch (error) {
                this.isAuthenticated = false;
                this.user = null;
            }
        }
    },
});
