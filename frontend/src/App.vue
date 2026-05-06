<template>
  <div class="app-wrapper">
    <!-- Login Page Layout -->
    <div v-if="isLoginPage">
      <RouterView />
    </div>

    <!-- Main Dashboard Layout -->
    <div v-else>
      <AppSidebar :is-open="sidebarOpen" @close="sidebarOpen = false" @logout="logout" />
      
      <div class="main-content">
        <AppHeader @toggle-sidebar="sidebarOpen = !sidebarOpen" />
        
        <main class="flex-grow-1 px-4 pb-4 pt-4 pt-lg-0 d-flex flex-column">
          <RouterView v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </RouterView>
        </main>
        
        <AppFooter
          :app-version="appVersion"
          :hitokoto-text="hitokotoText"
          @focus-version="handleVersionPillFocus"
        />
      </div>
    </div>
  </div>
  <ConfirmModal />
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AppSidebar from '@/components/layout/AppSidebar.vue';
import AppHeader from '@/components/layout/AppHeader.vue';
import AppFooter from '@/components/layout/AppFooter.vue';
import ConfirmModal from '@/components/common/ConfirmModal.vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

type ThemeMode = 'system' | 'dark' | 'light';

const isLoginPage = computed(() => route.path === '/login');
const sidebarOpen = ref(false);
const hitokotoText = ref('妹妹说紫色很有韵味！');
const isFetchingHitokoto = ref(false);

const getSystemPrefersDark = () => {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return true;
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
};

const applyTheme = () => {
  if (typeof document === 'undefined') {
    return;
  }

  const savedTheme = localStorage.getItem('theme');
  const themeMode: ThemeMode = savedTheme === 'light' || savedTheme === 'dark' || savedTheme === 'system'
    ? savedTheme
    : 'system';
  const shouldUseDark = themeMode === 'system' ? getSystemPrefersDark() : themeMode === 'dark';

  if (shouldUseDark) {
    document.body.classList.remove('light-theme');
  } else {
    document.body.classList.add('light-theme');
  }
};

const logout = async () => {
  await authStore.logout();
  router.push('/login');
};

const appVersion = ref('');

const fetchHitokoto = async () => {
  if (isFetchingHitokoto.value) {
    return;
  }

  isFetchingHitokoto.value = true;

  try {
    const response = await fetch('https://v1.hitokoto.cn/?encode=json');
    if (!response.ok) {
      throw new Error(`Failed to fetch hitokoto: ${response.status}`);
    }

    const data = await response.json();
    const from = data?.from ? ` —— ${data.from}` : '';
    hitokotoText.value = `${data?.hitokoto || '妹妹说紫色很有韵味！'}${from}`;
  } catch (error) {
    console.error('Failed to fetch hitokoto', error);
    hitokotoText.value = '妹妹说紫色很有韵味！';
  } finally {
    isFetchingHitokoto.value = false;
  }
};

const handleVersionPillFocus = () => {
  void fetchHitokoto();
};

watch(() => route.path, () => {
  applyTheme();
});

onMounted(async () => {
  applyTheme();
  void fetchHitokoto();

    try {
        // 使用后端 API 获取版本 (路由: /api/auth/version)
        const response = await fetch('/api/auth/version');
        if (response.ok) {
            const result = await response.json();
            // 适配 ApiResponse 格式：{ data: { version: "x.x.x" } }
            const version = result?.data?.version || result?.version;
            appVersion.value = 'v' + version;
        } else {
          appVersion.value = 'v2.2.1'; // Fallback
        }
    } catch (e) {
        console.error('Failed to fetch version', e);
        appVersion.value = 'v2.2.1'; // Fallback
    }
});
</script>

<style>
.app-wrapper {
  min-height: 100vh;
  height: 100vh;
  overflow: hidden;
}

.main-content > footer {
  margin-top: auto;
  padding-inline: 1.5rem;
}

.main-content > main {
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.main-content > footer p {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
}

.main-content {
  min-height: 100vh;
  height: 100vh;
  overflow: hidden;
}

@media (max-width: 767.98px) {
  .app-wrapper,
  .main-content {
    height: auto;
    overflow: visible;
  }

  .main-content > main {
    overflow-y: visible;
    padding-left: 0.7rem !important;
    padding-right: 0.7rem !important;
    padding-bottom: 0.85rem !important;
    padding-top: 0.85rem !important;
  }

  .main-content > footer {
    padding-inline: 0.7rem;
  }
}

.github-link {
  text-decoration: none !important;
  display: inline-flex;

  align-items: center;
  gap: 0.35rem;
  line-height: 1;
}

.github-link:hover {
  text-decoration: none !important;
}

.version-pill {
  cursor: help;
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 1.45rem;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  background: var(--bg-soft-primary);
  color: var(--primary-color);
  font-weight: 600;
  line-height: 1;
  outline: none;
}

.version-pill:focus-visible {
  box-shadow: 0 0 0 0.2rem rgba(var(--bs-primary-rgb), 0.2);
}

.easter-egg-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(10px);
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.75rem;
  font-size: 0.85rem;
  white-space: normal;
  text-align: center;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
  box-shadow: var(--shadow-active);
  z-index: 100;
  margin-bottom: 8px;
  font-weight: 500;
  letter-spacing: 0.02em;
  line-height: 1.55;
  min-width: 14rem;
  max-width: min(22rem, calc(100vw - 2rem));
}

.easter-egg-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: var(--primary-hover) transparent transparent transparent;
}

.version-pill:hover .easter-egg-tooltip,
.version-pill:focus-visible .easter-egg-tooltip {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
}

.star-1, .star-2, .star-3, .star-4 {
  position: absolute;
  color: #ffd66b;
  font-style: normal;
  animation: twinkle 1s infinite alternate;
  text-shadow: 0 0 5px rgba(255, 215, 0, 0.5);
}

.star-1 { top: -8px; left: -8px; animation-delay: 0s; font-size: 12px; }
.star-2 { top: -10px; right: 5px; animation-delay: 0.3s; font-size: 10px; }
.star-3 { bottom: -8px; left: 5px; animation-delay: 0.5s; font-size: 14px; }
.star-4 { bottom: -10px; right: -8px; animation-delay: 0.2s; font-size: 11px; }

@keyframes twinkle {
  0% { opacity: 0.3; transform: scale(0.8) rotate(0deg); }
  100% { opacity: 1; transform: scale(1.2) rotate(15deg); }
}
</style>
