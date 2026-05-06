import { createRouter, createWebHistory } from 'vue-router';
import { registerRouterGuards } from './guards';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/login',
            name: 'login',
            component: () => import('@/views/LoginView.vue'),
            meta: { guestOnly: true },
        },
        {
            path: '/',
            name: 'dashboard',
            component: () => import('@/views/DashboardView.vue'),
            meta: { requiresAuth: true },
            children: [
                {
                    path: '',
                    name: 'dashboard-home',
                    component: () => import('@/views/HomeView.vue'),
                },
                {
                    path: 'trackers',
                    name: 'trackers',
                    component: () => import('@/views/TrackersView.vue'),
                },
                {
                    path: 'hosts',
                    name: 'hosts',
                    component: () => import('@/views/HostsView.vue'),
                },
                {
                    path: 'clients',
                    name: 'clients',
                    component: () => import('@/views/ClientsView.vue'),
                },
                {
                    path: 'logs',
                    name: 'logs',
                    component: () => import('@/views/LogsView.vue'),
                },
                {
                    path: 'settings',
                    redirect: '/settings/system',
                },
                {
                    path: 'settings/system',
                    name: 'settings-system',
                    component: () => import('@/views/SystemView.vue'),
                },
                {
                    path: 'settings/about',
                    name: 'settings-about',
                    component: () => import('@/views/AboutView.vue'),
                },

                {
                    path: 'settings/notification',
                    name: 'settings-notification',
                    component: () => import('@/views/NotifyView.vue'),
                },

                {
                    path: 'settings/backup',
                    name: 'settings-backup',
                    component: () => import('@/views/BackupView.vue'),
                },
                {
                    path: 'settings/cfst',
                    name: 'settings-cfst',
                    component: () => import('@/views/CfstView.vue'),
                },

                {
                    path: 'settings/test',
                    redirect: '/settings/cfst',
                },
                {
                    path: 'settings/ikuai-dns',
                    name: 'settings-ikuai-dns',
                    component: () => import('@/views/IkuaiView.vue'),
                },

                {
                    path: 'settings/mihosts',
                    name: 'settings-mihosts',
                    component: () => import('@/views/MiHostsView.vue'),
                },

            ],
        },
        {
            path: '/:pathMatch(.*)*',
            redirect: '/',
        },
    ],
});

registerRouterGuards(router);

export default router;


