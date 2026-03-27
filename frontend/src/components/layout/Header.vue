<template>
  <!-- Header is now only for mobile sidebar toggle -->
  <header class="header d-flex align-items-center px-4 py-3 d-lg-none">
    <button class="btn btn-icon text-primary me-3" @click="$emit('toggle-sidebar')">
      <i class="bx bx-menu fs-4"></i>
    </button>
    <h5 class="header-title mb-0 fw-bold flex-grow-1">{{ pageTitle }}</h5>
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
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 1020;
  background: var(--bg-header);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--divider-color);
  box-shadow: 0 0.125rem 0.75rem rgba(67, 89, 113, 0.08);
}

.btn-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
  transition: all var(--transition-fast);
  border: none;
  background: var(--bg-soft-primary);
  margin-left: -10px; /* Align with padding */
}

.btn-icon:hover {
  background: rgba(var(--primary-rgb), 0.16);
  color: var(--primary-color) !important;
  transform: translateY(-1px);
}

.header-title {
  color: var(--text-heading);
  letter-spacing: -0.01em;
}
</style>
