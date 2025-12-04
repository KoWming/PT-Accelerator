<template>
  <div class="d-flex flex-column flex-grow-1 h-100">
    <div class="page-header flex-shrink-0">
      <h2 class="page-title">系统日志</h2>
      <Teleport to="#mobile-header-actions" :disabled="!isMobile">
        <div class="d-flex gap-2" v-if="isMobile || true">
          <button class="btn-pill btn-pill-primary" @click="fetchLogs" :disabled="loading">
            <span>
              <i class="bi bi-arrow-clockwise" :class="{ 'spin': loading, 'me-1': !isMobile }"></i> 
              <span v-if="!isMobile">刷新</span>
            </span>
          </button>
          <button class="btn-pill btn-pill-danger" @click="clearLogs" :disabled="clearing">
            <span>
              <i class="bi bi-trash" :class="{ 'me-1': !isMobile }"></i> 
              <span v-if="!isMobile">清空</span>
            </span>
          </button>
        </div>
      </Teleport>
    </div>

    <div class="card shadow-sm overflow-hidden d-flex flex-column flex-grow-1">
      <div class="card-body p-0 d-flex flex-column overflow-hidden">
        <div class="log-viewer flex-grow-1" ref="logContainer">
          <div v-if="parsedLogs.length === 0" class="text-center text-muted py-5">
            暂无日志
          </div>
          <div v-else>
            <div v-for="(log, index) in parsedLogs" :key="index" class="log-row">
              <div class="log-col-badge">
                <span class="log-badge" :class="getBadgeClass(log.level)">{{ log.level }}</span>
              </div>
              <div class="log-col-time">{{ log.time }}</div>
              <div class="log-col-module">{{ log.module }}</div>
              <div class="log-col-message" :class="getMessageClass(log.level)">{{ log.message }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed, watch } from 'vue';
import { useLogStore } from '../../stores/logs';
import { useMobile } from '../../composables/useMobile';
import { useConfirm } from '../../composables/useConfirm';

const store = useLogStore();
const { isMobile } = useMobile();
const { confirm } = useConfirm();
const logContainer = ref<HTMLElement | null>(null);
const loading = ref(false);
const clearing = ref(false);

// Regex to parse log lines: Time - Module - Level - Message
// Example: 2025-11-27 09:00:00,860 - invitessignin - ERROR - ...
const LOG_REGEX = /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (.*?) - (.*?) - (.*)$/;



const parsedLogs = computed<any[]>(() => {
  if (!store.logs) return [];
  
  const lines = store.logs.split('\n');
  const result: any[] = [];
  
  for (const line of lines) {
    if (!line.trim()) continue;
    
    const match = line.match(LOG_REGEX);
    if (match) {
      result.push({
        time: match[1],
        module: match[2],
        level: match[3],
        message: match[4]
      });
    } else {
      // Handle non-standard lines (e.g. stack traces) by appending to previous log or showing as raw
      // For simplicity, we'll treat them as raw info logs or append if possible
      // Here we just show them as raw text with empty fields
      result.push({
        time: '',
        module: '',
        level: 'RAW',
        message: line
      });
    }
  }
  
  // Usually logs are shown oldest to newest (top to bottom).
  // We want newest to oldest (top to bottom).
  return result.reverse();
});

const getBadgeClass = (level: string) => {
  const l = level.toUpperCase();
  if (l === 'ERROR') return 'log-badge-error';
  if (l === 'WARNING' || l === 'WARN') return 'log-badge-warning';
  if (l === 'INFO') return 'log-badge-info';
  if (l === 'DEBUG') return 'log-badge-debug';
  return 'bg-secondary';
};

const getMessageClass = (level: string) => {
  const l = level.toUpperCase();
  if (l === 'ERROR') return 'log-message-error';
  if (l === 'WARNING' || l === 'WARN') return 'log-message-warning';
  if (l === 'INFO') return 'log-message-info';
  if (l === 'DEBUG') return 'log-message-debug';
  return '';
};

const scrollToTop = () => {
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = 0;
    }
  });
};

const fetchLogs = async () => {
  loading.value = true;
  await store.fetchLogs();
  scrollToTop();
  loading.value = false;
};

const clearLogs = async () => {
  if (!await confirm('确定要清空所有日志吗？', '清空确认')) return;
  clearing.value = true;
  await store.clearLogs();
  await fetchLogs();
  clearing.value = false;
};

onMounted(async () => {
  await fetchLogs();
  scrollToTop();
});

watch(() => store.logs, () => {
  scrollToTop();
});
</script>

<style scoped>
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.log-viewer {
  height: 70vh;
}
</style>
