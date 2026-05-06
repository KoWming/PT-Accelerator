import axios, { type AxiosInstance } from 'axios';

const shouldRedirectToLogin = (error: any) => {
    const requestUrl = String(error?.config?.url || '');
    return !requestUrl.includes('/auth/login');
};

// Axios 实例 - 所有 API 统一使用 /api 前缀
const api: AxiosInstance = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,  // 启用 Cookie
    timeout: 30000,
});

// 响应拦截：处理 ApiResponse 格式和错误
api.interceptors.response.use(
    (response) => {
        // 兼容两类后端响应：
        // 1. ApiResponse: { success: true, data: ... }
        // 2. 业务原始响应: { success: true, message: ... } / { success: true, records: ... }
        const data = response.data;
        if (data && typeof data === 'object' && 'success' in data) {
            if (!data.success) {
                return Promise.reject(new Error(data.message || '请求失败'));
            }
            // 只有标准 ApiResponse 才解包 data；否则保留业务字段，避免吞掉 message/records 等结果
            if ('data' in data) {
                response.data = data.data;
            }
        }
        return response;
    },
    async (error) => {
        // 401 未授权
        if (error.response?.status === 401 && shouldRedirectToLogin(error)) {
            window.location.href = '/login';
        }
        // 403 禁止访问
        if (error.response?.status === 403) {
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// 认证专用实例（使用 /api 前缀，自动检测 Content-Type）
export const authApi: AxiosInstance = axios.create({
    baseURL: '/api',
    headers: {
        'Accept': 'application/json',
    },
    withCredentials: true,
    timeout: 30000,
});

authApi.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401 && shouldRedirectToLogin(error)) {
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default api;

