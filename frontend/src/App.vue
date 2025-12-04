<template>
  <div class="app-wrapper">
    <!-- Login Page Layout -->
    <div v-if="isLoginPage">
      <RouterView />
    </div>

    <!-- Main Dashboard Layout -->
    <div v-else>
      <Sidebar :is-open="sidebarOpen" @close="sidebarOpen = false" @logout="logout" />
      
      <div class="main-content">
        <Header @toggle-sidebar="sidebarOpen = !sidebarOpen" />
        
        <main class="flex-grow-1 px-4 pb-4 pt-4 pt-lg-0 d-flex flex-column">
          <RouterView v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </RouterView>
        </main>
        
        <footer class="text-center py-3 text-muted small">
          <p class="mb-0">
            PT-Accelerator &copy; {{ new Date().getFullYear() }}
            <span class="version-pill">
              v2.0.5
              <span class="easter-egg-tooltip">
                妹妹说紫色很有韵味！
                <i class="star-1">✦</i>
                <i class="star-2">★</i>
                <i class="star-3">✦</i>
                <i class="star-4">★</i>
              </span>
            </span>
            <a href="https://github.com/KoWming/PT-Accelerator" target="_blank" class="github-link">
              <i class="bi bi-github"></i>
              <span>GitHub</span>
            </a>
          </p>
        </footer>
      </div>
    </div>
  </div>
  <ConfirmModal />
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from './stores/auth';
import Sidebar from './components/layout/Sidebar.vue';
import Header from './components/layout/Header.vue';
import ConfirmModal from './components/ConfirmModal.vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const isLoginPage = computed(() => route.path === '/login');
const sidebarOpen = ref(false);

const logout = async () => {
  await authStore.logout();
  router.push('/login');
};
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.github-link {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.15rem 0.5rem;
  border-radius: 50rem;
  background: rgba(128, 128, 128, 0.1);
  border: 1px solid transparent;
  color: inherit;
  transition: all 0.2s ease;
  text-decoration: none !important;
  box-shadow: none !important; /* Override global a tag shadow */
  line-height: 1;
}

.github-link:hover {
  background: rgba(128, 128, 128, 0.2);
  color: var(--primary-color) !important;
  border-color: rgba(163, 112, 247, 0.3);
  transform: translateY(-1px);
}

/* Easter Egg Tooltip Styles */
.version-pill {
  cursor: help;
  position: relative;
  display: inline-block;
}

.easter-egg-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(10px);
  background: rgba(163, 112, 247, 0.9); /* Primary purple color */
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.85rem;
  white-space: nowrap; /* Prevent wrapping */
  text-align: center; /* Center text */
  opacity: 0;
  visibility: hidden;
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); /* Bouncy/smooth */
  pointer-events: none;
  box-shadow: 0 5px 15px rgba(163, 112, 247, 0.4);
  z-index: 100;
  margin-bottom: 8px;
  font-weight: bold;
  letter-spacing: 0.5px;
}

/* Arrow for tooltip */
.easter-egg-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: rgba(163, 112, 247, 0.9) transparent transparent transparent;
}

.version-pill:hover .easter-egg-tooltip {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
}

/* Twinkling Stars */
.star-1, .star-2, .star-3, .star-4 {
  position: absolute;
  color: #FFD700; /* Gold */
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
