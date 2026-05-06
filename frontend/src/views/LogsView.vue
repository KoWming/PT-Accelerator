<template>
  <div class="dashboard-redesign">
    <PageHeaderShell title="系统日志" :is-mobile="isMobile">
      <template #actions>
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
      </template>
    </PageHeaderShell>

    <section class="logs-layout">
      <article class="workspace-card logs-card">
        <header class="workspace-card-header logs-card-header">
          <div class="logs-card-heading">
            <div class="logs-card-title-row">
              <h3>
                日志流
                <span class="log-count">({{ filteredLogs.length }} / {{ parsedLogs.length }}条)</span>
              </h3>
              <span class="workspace-pill" :class="parsedLogs.length ? 'success' : 'danger'">
                <span class="workspace-pill-dot"></span>
                {{ parsedLogs.length ? 'READY' : 'EMPTY' }}
              </span>
            </div>
            <p>集中查看 IP 优选、Hosts 更新与调度任务执行记录，并按级别或关键词快速过滤。</p>
          </div>
        </header>

        <section class="logs-toolbar">
          <label class="logs-toolbar-field logs-toolbar-field-search">
            <span>关键词</span>
            <div class="logs-search-input">
              <i class="bx bx-search"></i>
              <input v-model.trim="searchKeyword" type="text" placeholder="搜索模块名、日志级别或消息内容" />
            </div>
          </label>

          <label class="logs-toolbar-field">
            <span>级别</span>
            <select v-model="selectedLevel">
              <option value="all">全部级别</option>
              <option value="ERROR">仅 ERROR</option>
              <option value="WARNING">仅 WARNING</option>
              <option value="INFO">仅 INFO</option>
              <option value="DEBUG">仅 DEBUG</option>
              <option value="RAW">仅 RAW</option>
            </select>
          </label>

          <label class="logs-toolbar-field">
            <span>读取条数</span>
            <select v-model="lineLimit" @change="fetchLogs">
              <option :value="200">最近 200 行</option>
              <option :value="500">最近 500 行</option>
              <option :value="1000">最近 1000 行</option>
              <option :value="2000">最近 2000 行</option>
            </select>
          </label>

          <button
            type="button"
            class="logs-toolbar-reset"
            @click="resetFilters"
            :disabled="selectedLevel === 'all' && !searchKeyword"
          >
            清空筛选
          </button>
        </section>

        <div class="log-viewer" ref="logContainer">
          <PageEmptyState
            v-if="parsedLogs.length === 0"
            container-class="logs-empty"
            icon="bx-file-blank"
            title="暂无日志"
            description="执行一次任务后，这里会展示完整运行记录。"
          />
          <PageEmptyState
            v-else-if="filteredLogs.length === 0"
            container-class="logs-empty logs-empty-filtered"
            icon="bx-filter-alt"
            title="当前筛选没有命中结果"
            description="试试放宽日志级别或清空关键词筛选。"
          />
          <div v-else class="log-stream">
            <div v-for="(log, index) in filteredLogs" :key="`${log.time}-${log.module}-${index}`" class="log-row" :class="[`level-${normalizeLevel(log.level).toLowerCase()}`]">
              <div class="log-col-meta">
                <div class="log-col-badge">
                  <span class="log-badge" :class="getBadgeClass(log.level)">{{ normalizeLevel(log.level) }}</span>
                </div>
                <div class="log-col-time mono-text">{{ log.time || '--' }}</div>
              </div>
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
import { useToast } from '@/composables/useToast';
import { useLogStore } from '@/stores/modules/logs';
import { useMobile } from '@/composables/useMobile';
import { useConfirm } from '@/composables/useConfirm';
import PageEmptyState from '@/components/shared/PageEmptyState.vue';
import PageHeaderShell from '@/components/shared/PageHeaderShell.vue';
import { getErrorMessage } from '@/utils/error';



interface ParsedLog {
  time: string;
  module: string;
  level: string;
  message: string;
}

const store = useLogStore();
const toast = useToast();
const { isMobile } = useMobile();
const { confirm } = useConfirm();
const logContainer = ref<HTMLElement | null>(null);
const loading = ref(false);
const clearing = ref(false);
const lineLimit = ref(1000);
const selectedLevel = ref<'all' | 'ERROR' | 'WARNING' | 'INFO' | 'DEBUG' | 'RAW'>('all');
const searchKeyword = ref('');


// Regex to parse log lines: Time - Module - Level - Message
// Backend format: %(asctime)s - %(name)s - %(levelname)s - %(message)s
// Example: 2026-04-20 14:31:45 - __main__ - INFO - message
const LOG_REGEX = /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (.+?) - (.+?) - (.*)$/;

const normalizeLevel = (level: string) => {
  const raw = String(level || '').trim().toUpperCase();
  if (raw === 'WARN') return 'WARNING';
  if (raw === 'ERR') return 'ERROR';
  return raw || 'RAW';
};

const parsedLogs = computed<ParsedLog[]>(() => {
  if (!store.logText) return [];

  const lines = store.logText.split('\n');
  const result: ParsedLog[] = [];

  for (const line of lines) {
    if (!line.trim()) continue;

    const match = line.match(LOG_REGEX);
    if (match) {
      result.push({
        time: match[1] || '',
        module: match[2] || '',
        level: normalizeLevel(match[3] || ''),
        message: match[4] || '',
      });
    } else {
      result.push({
        time: '',
        module: '',
        level: 'RAW',
        message: line,
      });
    }
  }

  return result.reverse();
});

const filteredLogs = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase();

  return parsedLogs.value.filter((log) => {
    const level = normalizeLevel(log.level);
    const matchesLevel = selectedLevel.value === 'all' || level === selectedLevel.value;
    if (!matchesLevel) return false;

    if (!keyword) return true;

    const haystack = `${log.time} ${log.module} ${level} ${log.message}`.toLowerCase();
    return haystack.includes(keyword);
  });
});

const getBadgeClass = (level: string) => {

  const l = normalizeLevel(level);
  if (l === 'ERROR') return 'log-badge-error';
  if (l === 'WARNING') return 'log-badge-warning';
  if (l === 'INFO') return 'log-badge-info';
  if (l === 'DEBUG') return 'log-badge-debug';
  return 'log-badge-raw';
};

const getMessageClass = (level: string) => {
  const l = normalizeLevel(level);
  if (l === 'ERROR') return 'log-message-error';
  if (l === 'WARNING') return 'log-message-warning';
  if (l === 'INFO') return 'log-message-info';
  if (l === 'DEBUG') return 'log-message-debug';
  return 'log-message-raw';
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
  try {
    await store.fetchLogs({ lines: lineLimit.value });
    scrollToTop();

  } catch (e: any) {
    const message = getErrorMessage(e, '读取失败');
    toast.error(`刷新日志失败：${message}`);
  } finally {
    loading.value = false;
  }
};

const clearLogs = async () => {
  if (!await confirm('确定要清空所有日志吗？', '清空确认')) return;
  clearing.value = true;
  try {
    await store.clearLogs();
    await fetchLogs();
    toast.success('日志已清空');
  } catch (e: any) {
    const message = getErrorMessage(e, '清空失败');
    toast.error(`清空日志失败：${message}`);
  } finally {
    clearing.value = false;
  }
};

const resetFilters = () => {
  selectedLevel.value = 'all';
  searchKeyword.value = '';
};

onMounted(async () => {
  await fetchLogs();
  scrollToTop();
});

watch(() => store.logText, () => {
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
  gap: 1.25rem;
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
  padding: 0.58rem 1rem;
  border-radius: 0.8rem;
  font-size: 0.84rem;
  margin-left: 0.25rem;
}

.action-btn-compact:first-child {
  margin-left: 0;
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

.logs-insight-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.85rem;
  margin-bottom: 1rem;
}

.logs-insight-card {
  display: grid;
  gap: 0.28rem;
  padding: 0.95rem 1rem;
  border-radius: 1rem;
  border: 1px solid var(--divider-color);
  background: color-mix(in srgb, var(--bg-surface) 92%, transparent);
}

.logs-insight-card-primary {
  border-color: rgba(var(--primary-rgb), 0.18);
  background: linear-gradient(180deg, rgba(var(--primary-rgb), 0.08), transparent 100%), color-mix(in srgb, var(--bg-surface) 92%, transparent);
}

.logs-insight-card span,
.logs-toolbar-field span {
  color: var(--text-muted);
  font-size: 0.76rem;
}

.logs-insight-card strong {
  color: var(--text-heading);
  font-size: 1.35rem;
  line-height: 1.1;
}

.logs-insight-card small {
  color: var(--text-muted);
  line-height: 1.45;
}

.logs-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) repeat(2, minmax(10rem, 0.7fr)) auto;
  gap: 0.85rem;
  align-items: end;
  margin-bottom: 1rem;
}

.logs-toolbar-field {
  display: grid;
  gap: 0.45rem;
}

.logs-search-input,
.logs-toolbar-field select {
  min-height: 2.85rem;
  border-radius: 0.9rem;
  border: 1px solid rgba(161, 172, 184, 0.18);
  background: color-mix(in srgb, var(--bg-surface-alt) 92%, transparent);
  color: var(--text-heading);
}

.logs-search-input {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0 0.9rem;
}

.logs-search-input i {
  color: var(--text-muted);
  font-size: 1rem;
}

.logs-search-input input {
  flex: 1 1 auto;
  min-width: 0;
  border: 0;
  background: transparent;
  color: inherit;
  outline: none;
}

.logs-toolbar-field select {
  padding: 0 0.9rem;
  outline: none;
}

.logs-search-input:focus-within,
.logs-toolbar-field select:focus {
  border-color: rgba(var(--primary-rgb), 0.28);
  box-shadow: 0 0 0 0.18rem rgba(var(--primary-rgb), 0.12);
}

.logs-toolbar-reset {
  min-height: 2.85rem;
  padding: 0.65rem 1rem;
  border: 1px solid rgba(var(--primary-rgb), 0.16);
  border-radius: 0.9rem;
  background: rgba(var(--primary-rgb), 0.08);
  color: var(--primary-color);
  font-weight: 600;
  transition: transform var(--transition-base), box-shadow var(--transition-base), background-color var(--transition-base), border-color var(--transition-base);
}

.logs-toolbar-reset:hover:not(:disabled),
.logs-toolbar-reset:focus-visible:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
  background: rgba(var(--primary-rgb), 0.12);
  border-color: rgba(var(--primary-rgb), 0.26);
  outline: none;
}

.logs-toolbar-reset:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.logs-feedback-panel {
  margin-bottom: 1rem;
  padding: 0.95rem 1rem;
  border-radius: 1rem;
  border: 1px solid rgba(var(--primary-rgb), 0.14);
  background: linear-gradient(180deg, rgba(var(--primary-rgb), 0.06), transparent 100%), var(--bg-surface-alt);
}

.logs-feedback-panel.is-success {
  border-color: rgba(74, 179, 126, 0.2);
  background: linear-gradient(180deg, rgba(74, 179, 126, 0.08), transparent 100%), var(--bg-surface-alt);
}

.logs-feedback-panel.is-error {
  border-color: rgba(225, 108, 108, 0.2);
  background: linear-gradient(180deg, rgba(225, 108, 108, 0.08), transparent 100%), var(--bg-surface-alt);
}

.logs-feedback-head {
  display: grid;
  gap: 0.3rem;
}

.logs-feedback-head strong {
  color: var(--text-heading);
  font-size: 0.95rem;
}

.logs-feedback-head span {
  color: var(--text-muted);
  line-height: 1.55;
}


.log-viewer {
  flex: 1 1 auto;
  min-height: 0;
  min-width: 0;
  height: 62vh;
  overflow: hidden;
  padding-right: 0;
  border-radius: 1rem;
  background: color-mix(in srgb, var(--bg-surface-alt) 94%, transparent);
  border: 1px solid rgba(161, 172, 184, 0.14);
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

.log-col-meta {
  display: contents;
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

.log-col-meta .log-col-time {
  width: 100%;
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

.log-badge-raw {
  color: #6b7280;
  background: rgba(107, 114, 128, 0.14);
}

.log-row.level-error {
  background: linear-gradient(90deg, rgba(225, 108, 108, 0.08), transparent 72%);
}

.log-row.level-warning {
  background: linear-gradient(90deg, rgba(255, 193, 7, 0.08), transparent 72%);
}

.log-message-raw {
  color: var(--text-muted);
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

@media (max-width: 767.98px) {
  .log-row {
    grid-template-columns: minmax(0, 1fr);
    row-gap: 0.55rem;
    align-items: start;
  }

  .log-col-meta {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 0.12rem;
    min-width: 0;
  }

  .log-col-badge {
    width: auto;
    justify-content: flex-start;
    flex-shrink: 0;
  }

  .log-col-time {
    padding-left: 0;
    margin-left: -0.1rem;
    width: auto;
    text-align: left;
    font-size: 0.8rem;
  }

  .log-col-module,
  .log-col-message {
    padding-left: 0;
  }
}

.mono-text {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

@media (max-width: 1200px) {
  .logs-insight-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .logs-toolbar {
    grid-template-columns: minmax(0, 1fr) repeat(2, minmax(9rem, 0.8fr));
  }

  .logs-toolbar-reset {
    grid-column: 1 / -1;
    justify-self: start;
  }

  .log-row {
    grid-template-columns: 3.4rem 10.6rem minmax(10.5rem, 11.2rem) minmax(0, 1fr);
  }
}

@media (max-width: 991.98px) {
  .logs-insight-grid,
  .logs-toolbar {
    grid-template-columns: 1fr;
  }

  .log-row {
    grid-template-columns: 1fr;
    row-gap: 0.55rem;
  }

  .log-col-meta {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 0.12rem;
    min-width: 0;
  }

  .log-col-badge {
    width: auto;
    justify-content: flex-start;
    flex-shrink: 0;
  }

  .log-col-time {
    padding-left: 0;
    margin-left: -0.1rem;
    width: auto;
    text-align: left;
    font-size: 0.8rem;
  }

  .log-col-module,
  .log-col-message {
    padding-left: 0;
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
