import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import LoginView from '../views/LoginView.vue';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/login',
            name: 'login',
            component: LoginView,
        },
        {
            path: '/',
            name: 'dashboard',
            component: () => import('../views/DashboardView.vue'),
            meta: { requiresAuth: true },
            children: [
                {
                    path: '',
                    name: 'dashboard-home',
                    component: () => import('../views/dashboard/Home.vue'),
                },
                {
                    path: 'trackers',
                    name: 'trackers',
                    component: () => import('../views/dashboard/Trackers.vue'),
                },
                {
                    path: 'hosts',
                    name: 'hosts',
                    component: () => import('../views/dashboard/Hosts.vue'),
                },
                {
                    path: 'clients',
                    name: 'clients',
                    component: () => import('../views/dashboard/Clients.vue'),
                },
                {
                    path: 'logs',
                    name: 'logs',
                    component: () => import('../views/dashboard/Logs.vue'),
                },
                {
                    path: 'settings',
                    redirect: '/settings/system',
                },
                {
                    path: 'settings/system',
                    name: 'settings-system',
                    component: () => import('../views/dashboard/Settings.vue'),
                },
                {
                    path: 'settings/notification',
                    name: 'settings-notification',
                    component: () => import('../views/dashboard/Settings.vue'),
                },
                {
                    path: 'settings/backup',
                    name: 'settings-backup',
                    component: () => import('../views/dashboard/Settings.vue'),
                },
            ],
        },
    ],
});

router.beforeEach(async (to, _from, next) => {
    const authStore = useAuthStore();

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        try {
            await authStore.checkAuth();
            if (authStore.isAuthenticated) {
                next();
            } else {
                next('/login');
            }
        } catch (e) {
            next('/login');
        }
    } else {
        next();
    }
});

export default router;
