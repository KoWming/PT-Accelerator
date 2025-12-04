<template>
  <aside class="sidebar" :class="{ 'sidebar-open': isOpen }">
    <div class="sidebar-header d-flex align-items-center justify-content-center py-4">
      <div class="d-flex align-items-center gap-2">
        <i class="bi bi-speedometer2 text-info fs-4"></i>
        <span class="fw-bold fs-5 text-info tracking-wide">PT-Accelerator</span>
      </div>
    </div>

    <div class="sidebar-content">
      <ul class="nav flex-column gap-1 px-3" ref="navListRef">
        <div class="nav-glider" :style="gliderStyle"></div>
        <li class="nav-item">
          <router-link to="/" class="nav-link d-flex align-items-center gap-3 px-3 py-3" exact-active-class="active">
            <i class="bi bi-grid fs-5"></i>
            <span>控制面板</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/logs" class="nav-link d-flex align-items-center gap-3 px-3 py-3" active-class="active">
            <i class="bi bi-journal-text fs-5"></i>
            <span>日志查看</span>
          </router-link>
        </li>
        
        <li class="nav-header mt-3 mb-2 px-3 text-uppercase text-muted small fw-bold">配置管理</li>
        
        <li class="nav-item">
          <router-link to="/clients" class="nav-link d-flex align-items-center gap-3 px-3 py-3" active-class="active">
            <i class="bi bi-hdd-network fs-5"></i>
            <span>下载器管理</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/hosts" class="nav-link d-flex align-items-center gap-3 px-3 py-3" active-class="active">
            <i class="bi bi-globe fs-5"></i>
            <span>Hosts源管理</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/trackers" class="nav-link d-flex align-items-center gap-3 px-3 py-3" active-class="active">
            <i class="bi bi-broadcast fs-5"></i>
            <span>Trackers管理</span>
          </router-link>
        </li>
        
        <li class="nav-header mt-3 mb-2 px-3 text-uppercase text-muted small fw-bold">系统</li>
        
        <li class="nav-item">
          <router-link to="/settings" class="nav-link d-flex align-items-center gap-3 px-3 py-3" active-class="active">
            <i class="bi bi-gear fs-5"></i>
            <span>系统设置</span>
          </router-link>
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
        
        <button class="btn btn-link text-main p-0 opacity-75 hover-opacity-100" @click="toggleTheme" title="切换主题">
          <i class="bi" :class="isDark ? 'bi-moon-stars' : 'bi-sun'"></i>
        </button>
        
        <button class="btn btn-link text-main p-0 opacity-75 hover-opacity-100" @click="$emit('logout')" title="退出登录">
          <i class="bi bi-box-arrow-right"></i>
        </button>
      </div>
    </div>
  </aside>
  
  <!-- Overlay for mobile -->
  <div class="sidebar-overlay" :class="{ 'show': isOpen }" @click="$emit('close')"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

defineProps<{
  isOpen: boolean
}>();

defineEmits(['close', 'logout']);

const route = useRoute();
const authStore = useAuthStore();
const isDark = ref(true);
const gliderStyle = ref({
  height: '0px',
  transform: 'translateY(0px)',
  opacity: 0
});
const navListRef = ref<HTMLElement | null>(null);

const username = computed(() => {
  return authStore.user?.username || 'Guest';
});

const userInitial = computed(() => {
  return username.value.charAt(0).toUpperCase();
});

const toggleTheme = () => {
  isDark.value = !isDark.value;
  updateTheme();
};

const updateTheme = () => {
  const body = document.body;
  if (isDark.value) {
    body.classList.remove('light-theme');
    localStorage.setItem('theme', 'dark');
  } else {
    body.classList.add('light-theme');
    localStorage.setItem('theme', 'light');
  }
};

const updateGlider = (retryCount = 0) => {
  if (!navListRef.value) return;
  
  // Find the active link within the nav list
  const activeLink = navListRef.value.querySelector('.nav-link.active') as HTMLElement;
  
  if (activeLink) {
    const listRect = navListRef.value.getBoundingClientRect();
    const linkRect = activeLink.getBoundingClientRect();
    
    const top = linkRect.top - listRect.top;
    const height = linkRect.height;
    
    gliderStyle.value = {
      height: `${height}px`,
      transform: `translateY(${top}px)`,
      opacity: 1
    };
  } else {
    // Retry if active link not found yet (e.g. on initial load/refresh)
    if (retryCount < 10) {
      setTimeout(() => updateGlider(retryCount + 1), 50);
      return;
    }
    
    gliderStyle.value = {
      ...gliderStyle.value,
      opacity: 0
    };
  }
};

// Watch for route changes to update glider
watch(() => route.path, () => {
  nextTick(() => {
    // Small delay to ensure DOM update and transition
    setTimeout(() => updateGlider(0), 50);
  });
}, { immediate: true });

onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    isDark.value = false;
    document.body.classList.add('light-theme');
  } else {
    isDark.value = true;
    document.body.classList.remove('light-theme');
  }
  
  // Initial glider update
  nextTick(() => {
    setTimeout(() => updateGlider(0), 100);
  });
  
  // Update on window resize
  window.addEventListener('resize', () => updateGlider(0));
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
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--glass-border);
  z-index: 1040;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, background-color 0.3s ease;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
}

.user-info-card {
  background: var(--bg-surface);
  border: 1px solid var(--glass-border);
  transition: all 0.2s ease;
}

.user-info-card:hover {
  background: rgba(var(--text-main), 0.05);
  border-color: var(--primary-color);
}

/* Nav List Container */
.nav {
  position: relative; /* For absolute positioning of glider */
}

/* The Glider */
.nav-glider {
  position: absolute;
  left: 1rem; /* Match px-3 (1rem) of ul, but wait, ul has px-3. 
                 If glider is in ul, left:0 starts at padding edge? No, content edge.
                 Let's check bootstrap px-3 is 1rem.
                 We want the glider to cover the link. Link has px-3 itself? No, link has px-3.
                 Let's adjust left/width to match the link's visual area.
                 Link is block, width 100%.
                 We'll set left: 0 and width: 100% of the UL content area? 
                 Actually, let's just set left: 0 and right: 0 inside the UL (which has padding).
                 Wait, UL has px-3. So content box is narrower. 
                 Glider at top:0 left:0 will be at top-left of content box.
                 Link is inside LI. LI has no padding. Link has px-3.
                 So glider should match Link's box.
              */
  top: 0;
  left: 1rem; /* Match ul padding-left if needed, or just 0 if appended to ul */
  right: 1rem;
  background: rgba(163, 112, 247, 0.15);
  box-shadow: 0 0 15px rgba(163, 112, 247, 0.1);
  border-radius: 0.5rem;
  z-index: 0;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); /* Smooth sliding */
  pointer-events: none;
}

body.light-theme .nav-glider {
  background: rgba(145, 85, 253, 0.15);
  box-shadow: 0 0 15px rgba(145, 85, 253, 0.1);
}

.nav-link {
  color: var(--text-muted);
  transition: color 0.2s ease;
  /* Reset global link styles */
  border: none;
  box-shadow: none;
  background: transparent !important; /* Remove background from link */
  border-radius: 0.5rem;
  position: relative;
  z-index: 1; /* Above glider */
}

.nav-link:hover {
  color: var(--text-main);
  /* background: rgba(var(--text-main), 0.05); Remove hover bg, maybe keep for non-active? */
}

/* Hover effect for non-active links */
.nav-link:not(.active):hover {
    background: rgba(var(--text-main), 0.05) !important;
}

.hover-opacity-100:hover {
  opacity: 1 !important;
}

.nav-link.active {
  color: var(--primary-color);
  font-weight: 600;
  /* Background handled by glider */
  box-shadow: none; 
}

.nav-link.active i {
  color: var(--primary-color);
}

body.light-theme .nav-link.active {
  color: var(--primary-color);
  background: transparent;
  box-shadow: none;
}

.x-small {
  font-size: 0.75rem;
}

/* Mobile Responsive */
@media (max-width: 991.98px) {
  .sidebar {
    transform: translateX(-100%);
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
    background: rgba(0, 0, 0, 0.5);
    z-index: 1030;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    backdrop-filter: blur(4px);
  }
  
  .sidebar-overlay.show {
    opacity: 1;
    visibility: visible;
  }
}
</style>
