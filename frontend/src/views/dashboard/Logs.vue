<template>
  <div class="dashboard-redesign">
    <div class="page-header">
      <h2 class="page-title">系统日志</h2>
      <Teleport to="#mobile-header-actions" :disabled="!isMobile">
        <div class="page-header-actions" v-if="isMobile || true">
          <button class="action-btn action-btn-primary action-btn-compact" @click="fetchLogs" :disabled="loading">
            <span>
              <i class="bx bx-refresh" :class="{ spin: loading }"></i>
              <span v-if="!isMobile">刷新日志</span>
            </span>
          </button>
          <button class="action-btn action-btn-danger action-btn-compact" @click="clearLogs" :disabled="clearing">
            <span>
              <i class="bx bx-trash"></i>
              <span v-if="!isMobile">清空日志</span>
            </span>
          </button>
        </div>
      </Teleport>
    </div>

    <section class="logs-layout">
      <article class="workspace-card logs-card">
        <header class="workspace-card-header logs-card-header">
          <div class="logs-card-heading">
            <div class="logs-card-title-row">
              <h3>
                日志流
                <span class="log-count">({{ parsedLogs.length }}条)</span>
              </h3>
              <span class="workspace-pill" :class="parsedLogs.length ? 'success' : 'danger'">
                <span class="workspace-pill-dot"></span>
                {{ parsedLogs.length ? 'READY' : 'EMPTY' }}
              </span>
            </div>
            <p>记录 IP 优选、Hosts 更新与调度任务的执行细节。</p>
          </div>
        </header>

        <div class="log-viewer" ref="logContainer">
          <div v-if="parsedLogs.length === 0" class="workspace-empty logs-empty">
            <i class="bx bx-file-blank"></i>
            <strong>暂无日志</strong>
            <span>执行一次任务后，这里会展示完整运行记录。</span>
          </div>
          <div v-else class="log-stream">
            <div v-for="(log, index) in parsedLogs" :key="index" class="log-row">
              <div class="log-col-badge">
                <span class="log-badge" :class="getBadgeClass(log.level)">{{ log.level }}</span>
              </div>
              <div class="log-col-time mono-text">{{ log.time || '--' }}</div>
              <div class="log-col-module">{{ log.module || 'system' }}</div>
              <div class="log-col-message" :class="getMessageClass(log.level)">{{ log.message }}</div>
            </div>
          </div>
        </div>
      </article>
    </section>
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
.dashboard-redesign {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-height: 0;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.12rem;
}

.page-header-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.logs-layout {
  display: flex;
  flex: 1 1 auto;
  min-height: 0;
  min-width: 0;
}

.workspace-card {
  min-width: 0;
  border-radius: 1.4rem;
  background: var(--bg-surface);
  border: 1px solid rgba(161, 172, 184, 0.14);
  box-shadow: var(--shadow-sm);
}

.logs-card {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  min-height: 0;
  min-width: 0;
  padding: 1.5rem;
  overflow: hidden;
}

.workspace-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.logs-card-header {
  align-items: center;
}

.logs-card-heading {
  flex: 1 1 240px;
  min-width: 0;
}

.logs-card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.85rem;
  flex-wrap: nowrap;
}

.logs-card-title-row .workspace-pill {
  flex-shrink: 0;
}

.workspace-card-header h3 {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-heading);
}

.log-count {
  font-size: 0.88rem;
  font-weight: 600;
  color: rgba(105, 122, 141, 0.72);
}

.workspace-card-header p {
  margin: 0.4rem 0 0;
  color: var(--text-muted);
  line-height: 1.65;
}

.workspace-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  min-width: 5.5rem;
  padding: 0.42rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.workspace-pill-dot {
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
}

.workspace-pill.success {
  color: var(--success-color);
  background: rgba(74, 179, 126, 0.14);
}

.workspace-pill.danger {
  color: var(--danger-color);
  background: rgba(225, 108, 108, 0.14);
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  border-radius: 0.95rem;
  padding: 0.8rem 1rem;
  font-weight: 600;
  font-size: 0.92rem;
  transition: transform var(--transition-base), box-shadow var(--transition-base), border-color var(--transition-base), background-color var(--transition-base);
}

.action-btn-compact {
  padding: 0.58rem 0.82rem;
  border-radius: 0.8rem;
  font-size: 0.84rem;
}

.action-btn-compact i {
  font-size: 1rem;
}

.action-btn span {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.action-btn:hover:not(:disabled),
.action-btn:focus-visible:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.action-btn:focus-visible {
  outline: none;
}

.action-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.action-btn-primary {
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
  border-color: rgba(var(--primary-rgb), 0.16);
}

.action-btn-primary:hover:not(:disabled),
.action-btn-primary:focus-visible:not(:disabled) {
  background: rgba(var(--primary-rgb), 0.14);
  border-color: rgba(var(--primary-rgb), 0.28);
}

.action-btn-danger {
  background: rgba(225, 108, 108, 0.1);
  color: var(--danger-color);
  border-color: rgba(225, 108, 108, 0.16);
}

.action-btn-danger:hover:not(:disabled),
.action-btn-danger:focus-visible:not(:disabled) {
  background: rgba(225, 108, 108, 0.14);
  border-color: rgba(225, 108, 108, 0.28);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.log-viewer {
  flex: 1 1 auto;
  min-height: 0;
  min-width: 0;
  height: 62vh;
  overflow: hidden;
  padding-right: 0;
  border-radius: 1rem;
}

.log-stream {
  display: flex;
  flex-direction: column;
  gap: 0;
  height: 100%;
  min-width: 0;
  overflow: auto;
  border-radius: inherit;
  scrollbar-gutter: stable;
}

.log-row {
  display: grid;
  grid-template-columns: 3.7rem 11.3rem minmax(12.2rem, 13rem) minmax(0, 1fr);
  column-gap: 0.7rem;
  row-gap: 0;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(161, 172, 184, 0.12);
  transition: background-color var(--transition-base);
}

.log-row:hover {
  background: rgba(161, 172, 184, 0.06);
}

.log-row:last-child {
  border-bottom: none;
}

.log-col-badge {
  display: flex;
  width: 100%;
  justify-content: center;
  align-items: center;
  min-width: 0;
}

.log-col-time,
.log-col-module,
.log-col-message {
  min-width: 0;
}

.log-col-time {
  padding-left: 0.26rem;
  color: var(--text-heading);
  font-size: 0.84rem;
}

.log-col-module {
  padding-right: 0.2rem;
  color: var(--text-muted);
  font-weight: 600;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.log-col-message {
  padding-left: 0.1rem;
  color: var(--text-heading);
  line-height: 1.7;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.log-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  min-width: 3.45rem;
  max-width: 100%;
  padding: 0.28rem 0.5rem;
  border-radius: 999px;
  font-size: 0.67rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

.log-badge-error {
  color: var(--danger-color);
  background: rgba(225, 108, 108, 0.14);
}

.log-badge-warning {
  color: #b7791f;
  background: rgba(255, 193, 7, 0.16);
}

.log-badge-info {
  color: #2d8da8;
  background: rgba(79, 183, 211, 0.16);
}

.log-badge-debug {
  color: var(--primary-color);
  background: rgba(var(--primary-rgb), 0.16);
}

.log-message-error {
  color: #b33f3f;
}

.log-message-warning {
  color: #9a6b16;
}

.log-message-info {
  color: var(--text-heading);
}

.log-message-debug {
  color: #566a7f;
}

.workspace-empty {
  min-height: 24rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: var(--text-muted);
  text-align: center;
}

.workspace-empty i {
  font-size: 2.2rem;
}

.workspace-empty strong {
  color: var(--text-heading);
  font-size: 1rem;
}

.mono-text {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

@media (max-width: 1200px) {
  .log-row {
    grid-template-columns: 3.4rem 10.6rem minmax(10.5rem, 11.2rem) minmax(0, 1fr);
  }
}

@media (max-width: 991.98px) {
  .log-row {
    grid-template-columns: 1fr;
    row-gap: 0.55rem;
  }
}

@media (max-width: 767.98px) {
  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .logs-card {
    padding: 1rem;
  }

  .log-viewer {
    height: auto;
    max-height: 70vh;
  }

  .log-row {
    grid-template-columns: 1fr;
  }

  .page-header-actions {
    width: 100%;
    order: 3;
  }

  .action-btn {
    flex: 1 1 0;
  }

  .logs-card-title-row {
    gap: 0.7rem;
  }
}
</style>
