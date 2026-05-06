<template>
  <div v-if="message" class="page-feedback-panel" :class="statusClass">
    <div class="page-feedback-head">
      <strong>{{ title }}</strong>
      <span>{{ message }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(defineProps<{
  title?: string;
  message?: string;
  status?: 'success' | 'error' | 'info' | '';
}>(), {
  title: '',
  message: '',
  status: '',
});

const statusClass = computed(() => (props.status ? `is-${props.status}` : ''));
</script>

<style scoped>
.page-feedback-panel {
  margin-bottom: 1rem;
  padding: 0.95rem 1rem;
  border-radius: 1rem;
  border: 1px solid rgba(161, 172, 184, 0.16);
  background: color-mix(in srgb, var(--bg-surface-alt) 92%, transparent);
}

.page-feedback-head {
  display: grid;
  gap: 0.28rem;
}

.page-feedback-head strong {
  color: var(--text-heading);
  font-size: 0.96rem;
}

.page-feedback-head span {
  color: var(--text-muted);
  line-height: 1.6;
}

.page-feedback-panel.is-success {
  border-color: rgba(74, 179, 126, 0.22);
  background: rgba(74, 179, 126, 0.08);
}

.page-feedback-panel.is-success .page-feedback-head strong {
  color: var(--success-color);
}

.page-feedback-panel.is-error {
  border-color: rgba(225, 108, 108, 0.24);
  background: rgba(225, 108, 108, 0.08);
}

.page-feedback-panel.is-error .page-feedback-head strong {
  color: var(--danger-color);
}

.page-feedback-panel.is-info {
  border-color: rgba(var(--primary-rgb), 0.22);
  background: rgba(var(--primary-rgb), 0.08);
}

.page-feedback-panel.is-info .page-feedback-head strong {
  color: var(--primary-color);
}
</style>
