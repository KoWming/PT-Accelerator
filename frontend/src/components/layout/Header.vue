<template>
  <!-- Header is now only for mobile sidebar toggle -->
  <header class="header d-flex align-items-center px-4 py-3 d-lg-none">
    <button class="btn btn-icon text-primary me-3" @click="$emit('toggle-sidebar')">
      <i class="bi bi-list fs-4"></i>
    </button>
    <h5 class="mb-0 fw-bold text-main flex-grow-1">{{ pageTitle }}</h5>
    <div id="mobile-header-actions" class="d-flex align-items-center gap-2"></div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

defineEmits(['toggle-sidebar']);

const route = useRoute();

const pageTitle = computed(() => {
  const name = route.name as string;
  switch (name) {
    case 'dashboard-home':
      return '控制面板';
    case 'logs':
      return '日志查看';
    case 'clients':
      return '下载器管理';
    case 'hosts':
      return 'Hosts源管理';
    case 'trackers':
      return 'Trackers管理';
    case 'settings':
      return '系统设置';
    default:
      return 'PT-Accelerator';
  }
});
</script>

<style scoped>
.header {
  height: 60px;
  position: sticky;
  top: 0;
  z-index: 1020;
  background: var(--bg-header);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--glass-border);
  box-shadow: var(--shadow-sm);
}

.btn-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
  border: none;
  background: transparent;
  margin-left: -10px; /* Align with padding */
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-main) !important;
}
</style>
