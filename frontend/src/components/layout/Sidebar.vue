<template>
  <aside class="sidebar" :class="{ 'sidebar-open': isOpen, 'sidebar-highlights-initializing': !hasInitializedHighlights }">
    <div class="sidebar-header">
      <div class="sidebar-brand d-flex align-items-center gap-3">
        <div class="brand-mark d-flex align-items-center justify-content-center">
          <i class="bx bx-layer brand-icon"></i>
        </div>
        <div class="brand-text-wrap">
          <span class="brand-title">PT-Accelerator</span>
        </div>
      </div>
    </div>

    <div class="sidebar-content">
      <ul ref="mainNavRef" class="nav flex-column px-3">
        <div v-if="mainHighlightVisible" class="nav-highlight nav-highlight-active" :class="{ 'nav-highlight-ready': highlightsReady }" :style="mainActiveHighlightStyle" aria-hidden="true"></div>
        <li class="nav-item">
          <router-link to="/" class="nav-link" exact-active-class="active" data-nav-key="dashboard">
            <i class="bx bx-grid-alt nav-icon"></i>
            <span class="nav-label">控制面板</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/logs" class="nav-link" active-class="active" data-nav-key="logs">
            <i class="bx bx-receipt nav-icon"></i>
            <span class="nav-label">日志查看</span>
          </router-link>
        </li>
        
        <li class="nav-header">
          <div class="title-wrapper">
            <span class="title-text">配置管理</span>
          </div>
        </li>
        
        <li class="nav-item">
          <router-link to="/clients" class="nav-link" active-class="active" data-nav-key="clients">
            <i class="bx bx-devices nav-icon"></i>
            <span class="nav-label">下载器管理</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/hosts" class="nav-link" active-class="active" data-nav-key="hosts">
            <i class="bx bx-globe nav-icon"></i>
            <span class="nav-label">Hosts源管理</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/trackers" class="nav-link" active-class="active" data-nav-key="trackers">
            <i class="bx bx-radar nav-icon"></i>
            <span class="nav-label">Trackers管理</span>
          </router-link>
        </li>
        
        <li class="nav-header">
          <div class="title-wrapper">
            <span class="title-text">系统功能</span>
          </div>
        </li>

        <li class="nav-item nav-group" :class="{ open: isSettingsGroupOpen }">
          <button type="button" class="nav-link nav-group-toggle" :class="{ active: isSettingsRoute }" data-nav-key="settings" @click="toggleSettingsGroup">
            <i class="bx bx-cog nav-icon"></i>
            <span class="nav-label">系统设置</span>
            <i class="bx bx-chevron-right nav-arrow"></i>
          </button>

          <div class="nav-group-children-wrapper">
            <div ref="settingsSubmenuRef" class="nav-submenu">
              <div v-if="subHighlightVisible" class="nav-sub-highlight nav-sub-highlight-active" :class="{ 'nav-highlight-ready': highlightsReady }" :style="subActiveHighlightStyle" aria-hidden="true"></div>
              <router-link to="/settings/system" class="nav-sublink" :class="{ active: isSettingsRoute && activeSettingsTab === 'system' }" data-subnav-key="system">
                <span class="nav-submenu-dot"></span>
                <span class="nav-label">安全与认证</span>
              </router-link>
              <router-link to="/settings/notification" class="nav-sublink" :class="{ active: isSettingsRoute && activeSettingsTab === 'notification' }" data-subnav-key="notification">
                <span class="nav-submenu-dot"></span>
                <span class="nav-label">通知渠道</span>
              </router-link>
              <router-link to="/settings/backup" class="nav-sublink" :class="{ active: isSettingsRoute && activeSettingsTab === 'backup' }" data-subnav-key="backup">
                <span class="nav-submenu-dot"></span>
                <span class="nav-label">备份设置</span>
              </router-link>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <div class="sidebar-footer p-3 mt-auto">
      <div class="user-info-card d-flex align-items-center gap-3 px-3 py-2 rounded-3">
        <div class="avatar rounded-circle d-flex align-items-center justify-content-center text-white fw-bold" style="width: 32px; height: 32px; background-color: #6f42c1;">
          {{ userInitial }}
        </div>
        <div class="flex-grow-1 overflow-hidden">
          <div class="text-main small fw-bold text-truncate">{{ username }}</div>
          <div class="text-muted x-small text-truncate">Online</div>
        </div>
        
        <button class="btn btn-link text-main p-0 opacity-75 hover-opacity-100" @click="toggleTheme" :title="themeToggleTitle">
          <i class="bx" :class="themeIconClass"></i>
        </button>
        
        <button class="btn btn-link text-main p-0 opacity-75 hover-opacity-100" @click="$emit('logout')" title="退出登录">
          <i class="bx bx-log-out"></i>
        </button>
      </div>
    </div>
  </aside>
  
  <!-- Overlay for mobile -->
  <div class="sidebar-overlay" :class="{ 'show': isOpen }" @click="$emit('close')"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed, nextTick, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

type ThemeMode = 'system' | 'dark' | 'light';

defineProps<{
  isOpen: boolean
}>();

defineEmits(['close', 'logout']);

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const MOBILE_BREAKPOINT = 767.98;
const isDark = ref(true);
const themeMode = ref<ThemeMode>('system');
const isMobileViewport = ref(false);
const isSettingsGroupOpen = ref(false);
const highlightsReady = ref(false);
const hasInitializedHighlights = ref(false);
const mainHighlightVisible = ref(false);
const subHighlightVisible = ref(false);
const mainNavRef = ref<HTMLElement | null>(null);
const settingsSubmenuRef = ref<HTMLElement | null>(null);
const mainActiveHighlightStyle = ref<Record<string, string>>({ opacity: '0' });
const subActiveHighlightStyle = ref<Record<string, string>>({ opacity: '0' });

const username = computed(() => {
  const name = authStore.user?.username || 'Guest';
  if (name.toLowerCase() === 'guest') {
    return 'guest';
  }
  return name;
});

const userInitial = computed(() => {
  return username.value.charAt(0).toUpperCase();
});

const isSettingsRoute = computed(() => route.path.startsWith('/settings'));
const activeMainKey = computed(() => {
  if (route.path === '/') return 'dashboard';
  if (route.path.startsWith('/logs')) return 'logs';
  if (route.path.startsWith('/clients')) return 'clients';
  if (route.path.startsWith('/hosts')) return 'hosts';
  if (route.path.startsWith('/trackers')) return 'trackers';
  if (route.path.startsWith('/settings')) return 'settings';
  return '';
});

const activeSettingsTab = computed(() => {
  if (!isSettingsRoute.value) return '';
  if (route.path.startsWith('/settings/notification')) return 'notification';
  if (route.path.startsWith('/settings/backup')) return 'backup';
  return 'system';
});

const themeIconClass = computed(() => {
  if (themeMode.value === 'system') {
    return 'bx-desktop';
  }
  return isDark.value ? 'bx-moon' : 'bx-sun';
});

const themeToggleTitle = computed(() => {
  if (themeMode.value === 'system') {
    return '当前跟随系统主题，点击切换为深色主题';
  }
  if (themeMode.value === 'dark') {
    return '当前为深色主题，点击切换为浅色主题';
  }
  return '当前为浅色主题，点击切换为跟随系统主题';
});

const updateViewportState = () => {
  if (typeof window === 'undefined') return;
  isMobileViewport.value = window.innerWidth <= MOBILE_BREAKPOINT;
};

const updateHighlight = (container: HTMLElement | null, selector: string, styleRef: { value: Record<string, string> }, options?: { insetTop?: number; insetX?: number; radius?: string }) => {
  if (!container) {
    styleRef.value = { opacity: '0' };
    return false;
  }

  const target = container.querySelector<HTMLElement>(selector);
  if (!target) {
    styleRef.value = { opacity: '0' };
    return false;
  }

  const containerRect = container.getBoundingClientRect();
  const targetRect = target.getBoundingClientRect();
  const insetTop = options?.insetTop ?? 0;
  const insetX = options?.insetX ?? 0;

  styleRef.value = {
    opacity: '1',
    top: `${targetRect.top - containerRect.top + insetTop}px`,
    left: `${targetRect.left - containerRect.left + insetX}px`,
    width: `${Math.max(targetRect.width - insetX * 2, 0)}px`,
    height: `${targetRect.height - insetTop * 2}px`,
    borderRadius: options?.radius ?? '0.375rem'
  };

  return true;
};

const syncMainActiveHighlight = () => {
  if (activeMainKey.value) {
    const found = updateHighlight(mainNavRef.value, `[data-nav-key="${activeMainKey.value}"]`, mainActiveHighlightStyle, { radius: '0.375rem' });
    mainHighlightVisible.value = found;
    return found;
  }
  mainHighlightVisible.value = false;
  mainActiveHighlightStyle.value = { opacity: '0' };
  return false;
};

const syncSubActiveHighlight = () => {
  if (isSettingsRoute.value && isSettingsGroupOpen.value) {
    const found = updateHighlight(settingsSubmenuRef.value, `[data-subnav-key="${activeSettingsTab.value}"]`, subActiveHighlightStyle, { radius: '0.375rem' });
    subHighlightVisible.value = found;
    return found;
  }
  subHighlightVisible.value = false;
  subActiveHighlightStyle.value = { opacity: '0' };
  return false;
};

const syncNavHighlights = async () => {
  await nextTick();
  const mainFound = syncMainActiveHighlight();
  const subFound = syncSubActiveHighlight();
  return { mainFound, subFound };
};

const initializeHighlights = async () => {
  highlightsReady.value = false;
  hasInitializedHighlights.value = false;
  mainHighlightVisible.value = false;
  subHighlightVisible.value = false;

  await router.isReady();
  syncSettingsGroup();

  for (let attempt = 0; attempt < 8; attempt += 1) {
    const { mainFound, subFound } = await syncNavHighlights();
    const isReady = mainFound && (!isSettingsRoute.value || !isSettingsGroupOpen.value || subFound);
    if (isReady) {
      break;
    }
    await new Promise<void>((resolve) => {
      requestAnimationFrame(() => resolve());
    });
  }

  await nextTick();
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      hasInitializedHighlights.value = true;
      highlightsReady.value = true;
    });
  });
};

const syncSettingsGroup = () => {
  if (isSettingsRoute.value) {
    isSettingsGroupOpen.value = true;
    return;
  }
  isSettingsGroupOpen.value = !isMobileViewport.value;
};

const toggleSettingsGroup = () => {
  isSettingsGroupOpen.value = !isSettingsGroupOpen.value;
};

const toggleTheme = () => {
  if (themeMode.value === 'system') {
    themeMode.value = 'dark';
  } else if (themeMode.value === 'dark') {
    themeMode.value = 'light';
  } else {
    themeMode.value = 'system';
  }
  updateTheme();
};

const getSystemPrefersDark = () => {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return true;
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
};

const updateTheme = () => {
  const body = document.body;
  const shouldUseDark = themeMode.value === 'system' ? getSystemPrefersDark() : themeMode.value === 'dark';

  isDark.value = shouldUseDark;

  if (shouldUseDark) {
    body.classList.remove('light-theme');
  } else {
    body.classList.add('light-theme');
  }

  localStorage.setItem('theme', themeMode.value);
};

const handleSystemThemeChange = () => {
  if (themeMode.value !== 'system') {
    return;
  }
  updateTheme();
};

const handleResize = () => {
  updateViewportState();
  syncSettingsGroup();
  void syncNavHighlights();
};

watch(() => route.path, () => {
  if (!hasInitializedHighlights.value) {
    return;
  }
  syncSettingsGroup();
  void syncNavHighlights();
});

watch(isSettingsGroupOpen, () => {
  if (!hasInitializedHighlights.value) {
    return;
  }
  void syncNavHighlights();
});

onMounted(async () => {
  updateViewportState();

  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light' || savedTheme === 'dark' || savedTheme === 'system') {
    themeMode.value = savedTheme;
  } else {
    themeMode.value = 'system';
  }

  updateTheme();

  if (typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', handleSystemThemeChange);
  }

  syncSettingsGroup();
  await initializeHighlights();
  window.addEventListener('resize', handleResize);
});

onBeforeUnmount(() => {
  if (typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
    window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', handleSystemThemeChange);
  }
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 260px;
  background: var(--bg-sidebar);
  backdrop-filter: blur(18px);
  border-right: 1px solid var(--glass-border);
  z-index: 1040;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-slow), background-color var(--transition-slow), box-shadow var(--transition-base);
}

.sidebar-header {
  padding: 1.375rem 1.5rem 0.875rem;
}

.sidebar-brand {
  min-height: 4rem;
}

.brand-mark {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 0.85rem;
  position: relative;
  overflow: hidden;
  color: var(--primary-color);
  background: linear-gradient(135deg, rgba(var(--primary-rgb), 0.18), rgba(var(--primary-rgb), 0.08));
  box-shadow: inset 0 0 0 1px rgba(var(--primary-rgb), 0.12);
  animation: brandMarkBreath 3.2s ease-in-out infinite;
}

.brand-mark::after {
  content: '';
  position: absolute;
  inset: 0.3rem;
  border-radius: 0.7rem;
  background: radial-gradient(circle at center, rgba(var(--primary-rgb), 0.18), transparent 72%);
  opacity: 0.78;
  animation: brandGlowBreath 3.2s ease-in-out infinite;
}

.brand-icon {
  position: relative;
  z-index: 1;
  font-size: 1.5rem;
  line-height: 1;
  color: var(--primary-color);
  filter: drop-shadow(0 0 8px rgba(var(--primary-rgb), 0.24));
  animation: brandIconBreath 3.2s ease-in-out infinite;
}

@keyframes brandMarkBreath {
  0%,
  100% {
    transform: scale(1);
    box-shadow: inset 0 0 0 1px rgba(var(--primary-rgb), 0.12), 0 0 0 rgba(var(--primary-rgb), 0);
  }
  50% {
    transform: scale(1.035);
    box-shadow: inset 0 0 0 1px rgba(var(--primary-rgb), 0.2), 0 0.5rem 1.4rem rgba(var(--primary-rgb), 0.22);
  }
}

@keyframes brandGlowBreath {
  0%,
  100% {
    opacity: 0.52;
    transform: scale(0.92);
  }
  50% {
    opacity: 0.96;
    transform: scale(1.12);
  }
}

@keyframes brandIconBreath {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.9;
  }
  50% {
    transform: scale(1.12);
    opacity: 1;
  }
}

@keyframes navJellySlide {
  0% {
    transform: translateX(0) scaleX(1) scaleY(1);
  }
  35% {
    transform: translateX(3px) scaleX(1.04) scaleY(0.94);
  }
  65% {
    transform: translateX(-1px) scaleX(0.985) scaleY(1.03);
  }
  100% {
    transform: translateX(2px) scaleX(1) scaleY(1);
  }
}

@keyframes navJellyIndicator {
  0% {
    transform: translateY(-50%) scaleY(0.82);
  }
  45% {
    transform: translateY(-50%) scaleY(1.12);
  }
  75% {
    transform: translateY(-50%) scaleY(0.94);
  }
  100% {
    transform: translateY(-50%) scaleY(1);
  }
}

.brand-text-wrap {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.brand-title {
  color: var(--text-heading);
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.01em;
}

.brand-subtitle {
  margin-top: 0.2rem;
  color: var(--text-muted);
  font-size: 0.75rem;
  letter-spacing: 0.04em;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding-block: 0.25rem 1rem;
}

.user-info-card {
  background: var(--bg-surface-alt);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-xs);
  transition: all var(--transition-fast);
}

.user-info-card:hover {
  border-color: rgba(var(--primary-rgb), 0.24);
  box-shadow: var(--shadow-sm);
}

.nav {
  position: relative;
}

.nav-highlight,
.nav-sub-highlight {
  position: absolute;
  z-index: 0;
  pointer-events: none;
  opacity: 0;
  background: rgba(163, 112, 247, 0.1);
}

.nav-highlight-ready {
  transition: top 0.42s cubic-bezier(0.22, 1.22, 0.36, 1), left 0.42s cubic-bezier(0.22, 1.22, 0.36, 1), width 0.42s cubic-bezier(0.22, 1.22, 0.36, 1), height 0.42s cubic-bezier(0.22, 1.22, 0.36, 1), opacity 0.2s ease;
}

body.light-theme .nav-highlight,
body.light-theme .nav-sub-highlight {
  background: rgba(145, 85, 253, 0.1);
}

.nav-item {
  margin-bottom: 0.25rem;
}

.nav-group {
  margin-bottom: 0.25rem;
}

.nav-group-children-wrapper {
  overflow: hidden;
}

.nav-group-children-wrapper {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.3s ease-in-out;
}

.nav-group.open .nav-group-children-wrapper {
  grid-template-rows: 1fr;
}

.nav-link {
  display: flex;
  align-items: center;
  min-height: 2.625rem;
  width: 100%;
  padding: 0.53125rem 1rem;
  gap: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
  transition: color var(--transition-fast), background-color var(--transition-fast), box-shadow var(--transition-fast);
  border: none;
  box-shadow: none;
  background: transparent;
  border-radius: 0.375rem;
  position: relative;
  z-index: 1;
  text-decoration: none;
}

.nav-link::after {
  content: '';
  position: absolute;
  top: 50%;
  right: -0.75rem;
  width: 0.25rem;
  height: 2.625rem;
  border-top-left-radius: 0.375rem;
  border-bottom-left-radius: 0.375rem;
  background: var(--primary-color);
  transform: translateY(-50%);
  opacity: 0;
  transition: opacity var(--transition-fast), transform 0.34s cubic-bezier(0.22, 1, 0.36, 1);
}

.nav-group-toggle {
  width: 100%;
}

.nav-group-toggle.active {
  color: var(--primary-color);
}

.nav-group-toggle.active::after {
  opacity: 0;
}

.nav-icon {
  flex-shrink: 0;
  width: 1.5rem;
  font-size: 1.25rem;
  line-height: 1;
  color: currentColor;
}

.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.2;
}

.nav-arrow {
  margin-left: auto;
  font-size: 1.1rem;
  color: currentColor;
  transition: transform var(--transition-fast);
}

.nav-group.open .nav-arrow {
  transform: rotate(90deg);
}

.nav-submenu {
  overflow: hidden;
  position: relative;
  margin: 0.125rem 0 0.375rem;
  padding: 0.375rem 0 0;
}

.nav-sublink {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-height: 2.625rem;
  padding: 0.53125rem 1rem;
  border-radius: 0;
  color: var(--text-muted);
  font-size: 0.875rem;
  font-weight: 500;
  position: relative;
  z-index: 1;
  text-decoration: none;
  background: transparent;
  border: 0 !important;
  box-shadow: none !important;
  transition: color var(--transition-fast);
}

.nav-sublink:hover {
  color: var(--text-heading);
  background: transparent !important;
  box-shadow: none !important;
}

.nav-sublink.active {
  color: var(--primary-color);
  font-weight: 600;
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

.nav-submenu-dot {
  width: 1.5rem;
  height: 1.25rem;
  flex-shrink: 0;
  position: relative;
}

.nav-submenu-dot::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  display: block;
  width: 0.42rem;
  height: 0.42rem;
  border-radius: 999px;
  background: currentColor;
  opacity: 0.75;
  transition: transform 0.34s cubic-bezier(0.22, 1, 0.36, 1), opacity var(--transition-fast);
}

.nav-link:hover,
.nav-link:focus-visible,
.nav-group-toggle:active {
  color: var(--text-heading);
}

.hover-opacity-100:hover {
  opacity: 1 !important;
}

.nav-link.active {
  color: var(--primary-color);
  font-weight: 600;
  box-shadow: none;
  background: transparent !important;
}

.sidebar-highlights-initializing .nav-link.active {
  background: rgba(163, 112, 247, 0.1) !important;
}

.nav-link.active::after {
  opacity: 1;
  animation: navJellyIndicator 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}

.nav-link.active i {
  color: var(--primary-color);
}

.nav-sublink:hover .nav-submenu-dot::before,
.nav-sublink:focus-visible .nav-submenu-dot::before,
.nav-sublink.active .nav-submenu-dot::before {
  transform: translate(-50%, -50%) scale(1.22);
  opacity: 1;
}

body.light-theme .nav-link.active {
  color: var(--primary-color);
  box-shadow: none;
  background: transparent !important;
}

body.light-theme .sidebar-highlights-initializing .nav-link.active {
  background: rgba(145, 85, 253, 0.1) !important;
}

.sidebar-highlights-initializing .nav-sublink.active {
  background: rgba(163, 112, 247, 0.1) !important;
}

body.light-theme .sidebar-highlights-initializing .nav-sublink.active {
  background: rgba(145, 85, 253, 0.1) !important;
}

.x-small {
  font-size: 0.75rem;
}

.nav-header {
  margin: 1.5rem 0.9375rem 0.5rem !important;
  padding: 0;
  min-height: 1.5rem;
  overflow: hidden;
}

.nav-header:first-of-type {
  margin-top: 0.75rem !important;
}

.title-wrapper {
  min-height: 1.5rem;
  overflow: hidden;
}

.title-text {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  column-gap: 0.75rem;
  font-size: 0.75rem;
  line-height: 1;
  letter-spacing: 0.4px;
  font-weight: 500;
  color: #a8acb8;
  text-transform: uppercase;
  white-space: nowrap;
  opacity: 0.95;
}

.title-text::before {
  content: '';
  flex: 0 0 1.5rem;
  min-width: 1.5rem;
  max-width: 1.5rem;
  border-bottom: 1px solid rgba(161, 172, 184, 0.32);
  margin-left: 0;
}

.nav-header .title-wrapper {
  padding-left: 0;
}

body.light-theme .title-text {
  color: #8f96a3;
}

body.light-theme .title-text::before {
  border-bottom-color: rgba(143, 150, 163, 0.3);
}

.avatar {
  box-shadow: 0 0.25rem 0.75rem rgba(var(--primary-rgb), 0.35);
}

@media (max-width: 991.98px) {
  .sidebar {
    transform: translateX(-100%);
    box-shadow: none;
  }
  
  .sidebar.sidebar-open {
    transform: translateX(0);
  }
  
  .sidebar-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--bg-overlay);
    z-index: 1030;
    opacity: 0;
    visibility: hidden;
    transition: all var(--transition-slow);
    backdrop-filter: blur(4px);
  }
  
  .sidebar-overlay.show {
    opacity: 1;
    visibility: visible;
  }
}
</style>
