<template>
  <div class="dashboard-redesign">
    <div class="page-header">
      <h2 class="page-title">控制面板</h2>
    </div>

    <section class="insight-grid">
      <section class="config-stage compact-stage">
        <div class="config-stage-head">
          <div class="config-stage-heading">
            <div class="config-stage-title-row">
              <h3>任务调度配置</h3>
              <span class="workspace-pill" :class="schedulerRunning ? 'success' : 'danger'">
                <span class="workspace-pill-dot"></span>
                {{ schedulerRunning ? 'ACTIVE' : 'STOPPED' }}
              </span>
            </div>
          </div>
        </div>

        <div v-if="jobs.length === 0" class="workspace-empty config-workflow-empty">
            <i class="bx bx-inbox"></i>
            <span>当前没有待展示的调度任务</span>
        </div>

        <div v-else class="workflow-stack config-workflow-stack">
          <article class="workflow-node" v-for="job in jobs" :key="job.name">
            <div class="workflow-node-marker">
              <i class="bx bx-calendar-check"></i>
            </div>
            <div class="workflow-node-body">
              <div class="workflow-node-top">
                <h4>{{ job.name }}</h4>
                <span class="mono-text workflow-next-run">{{ job.next_run }}</span>
              </div>
              <p class="workflow-node-desc">系统将在预设时间触发该任务，并在日志页面记录完整执行过程。</p>
            </div>
          </article>
        </div>

        <form @submit.prevent="saveCloudflareSettings" class="config-stage-body compact-stage-body">
          <div class="config-editor-shell">
            <div class="toggle-row">
              <label class="switch me-3">
                <input type="checkbox" v-model="cfConfig.enable">
                <div class="slider">
                  <div class="circle">
                    <svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg">
                      <g>
                        <path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path>
                      </g>
                    </svg>
                    <svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg">
                      <g>
                        <path class="" data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path>
                      </g>
                    </svg>
                  </div>
                </div>
              </label>
              <div>
                <strong>启用定时任务</strong>
                <p>关闭后将暂停自动调度，仅保留手动执行能力。</p>
              </div>
            </div>

            <div class="config-field">
              <label class="form-label">CRON 表达式</label>
              <CronInput v-model="cfConfig.cron" />
              <small>
                默认值：<span class="mono-text">0 0 * * *</span>，表示每天零点执行。
              </small>
            </div>
            <button type="submit" class="save-config-btn" :disabled="savingCf">
              <span>
                <span v-if="savingCf" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bx bx-save me-2"></i>
                保存配置
              </span>
            </button>
          </div>
        </form>
      </section>

      <article class="workspace-card workspace-card-side">
        <header class="workspace-card-header compact">
          <div>
            <h3>快捷操作</h3>
          </div>
        </header>

        <div class="action-tile-list">
          <button class="action-tile action-tile-primary" @click="runCloudflareTest" :disabled="runningCf">
            <i class="bx bx-rocket"></i>
            <div>
              <strong>运行 IP 优选</strong>
              <span>启动 IP 优选与 Hosts 更新任务</span>
            </div>
          </button>

          <button class="action-tile action-tile-success" @click="updateHosts" :disabled="updatingHosts">
            <i class="bx bx-world"></i>
            <div>
              <strong>仅更新 Hosts</strong>
              <span>保留既有配置，仅刷新 Hosts 内容</span>
            </div>
          </button>

          <button class="action-tile action-tile-danger" @click="handleClearAndUpdate" :disabled="clearing">
            <i class="bx bx-trash"></i>
            <div>
              <strong>清空并重建</strong>
              <span>清理项目写入的分区后重新生成</span>
            </div>
          </button>
        </div>

        <div class="notice-panel">
          <h4><i class="bx bx-bulb"></i> 操作建议</h4>
          <ul>
            <li>运行任务后建议到日志页查看执行结果。</li>
            <li>修改 CRON 并保存后会立即生效。</li>
            <li>清空操作会覆盖项目写入的 Hosts 分区。</li>
          </ul>
        </div>
      </article>
    </section>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive } from 'vue';
import axios from '../../api/axios';
import { useTrackerStore } from '../../stores/trackers';
import { useHostsStore } from '../../stores/hosts';
import CronInput from '../../components/CronInput.vue';
import { useToast } from 'vue-toastification';
import { useConfirm } from '../../composables/useConfirm';

const trackerStore = useTrackerStore();
const hostsStore = useHostsStore();
const toast = useToast();
const { confirm } = useConfirm();

const schedulerRunning = ref(false);
const jobs = ref<any[]>([]);
const runningCf = ref(false);
const updatingHosts = ref(false);
const clearing = ref(false);
const savingCf = ref(false);
const cfConfig = reactive({
  enable: true,
  cron: '0 0 * * *'
});

const getWorkflowJobs = (schedulerJobs: any[], config: any) => {
  const normalizedJobs = Array.isArray(schedulerJobs) ? [...schedulerJobs] : [];
  const backupConfig = config?.backup || {};
  const backupEnabled = Boolean(backupConfig.enable);
  const hasBackupJob = normalizedJobs.some(job => {
    const id = String(job?.id || '');
    const name = String(job?.name || '');
    return id.includes('backup') || name.includes('备份');
  });

  if (backupEnabled && !hasBackupJob) {
    normalizedJobs.push({
      id: 'backup_config_task',
      name: '配置备份定时任务',
      next_run: '未安排'
    });
  }

  return normalizedJobs;
};

onMounted(async () => {
  await fetchStatus();
  await trackerStore.fetchConfig();
  cfConfig.enable = trackerStore.cloudflare.enable;
  cfConfig.cron = trackerStore.cloudflare.cron;
});

onUnmounted(() => {
});

const fetchStatus = async () => {
  try {
    const [statusResponse, configResponse] = await Promise.all([
      axios.get('/scheduler-status'),
      axios.get('/config')
    ]);
    schedulerRunning.value = statusResponse.data.running;
    jobs.value = getWorkflowJobs(statusResponse.data.jobs || [], configResponse.data);
  } catch (e) {
    console.error('Failed to fetch status', e);
  }
};

const runCloudflareTest = async () => {
  runningCf.value = true;
  try {
    await axios.post('/run-cloudflare-test');
    toast.success('IP 优选任务已启动（后台运行）');
    setTimeout(fetchStatus, 2000);
  } catch (e) {
    toast.error('启动失败');
  } finally {
    runningCf.value = false;
  }
};

const updateHosts = async () => {
  updatingHosts.value = true;
  try {
    await axios.post('/update-hosts');
    toast.success('Hosts 更新成功');
  } catch (e) {
    toast.error('更新失败');
  } finally {
    updatingHosts.value = false;
  }
};

const handleClearAndUpdate = async () => {
  if (!await confirm('确定要清理由本项目写入的 hosts 分区并重新生成吗？', '清理确认')) return;
  clearing.value = true;
  try {
    await hostsStore.clearAndUpdateHosts();
    toast.success('清理并更新成功');
  } catch (e) {
    toast.error('操作失败');
  } finally {
    clearing.value = false;
  }
};

const saveCloudflareSettings = async () => {
  savingCf.value = true;
  try {
    await trackerStore.saveCloudflareConfig({ ...cfConfig });
    toast.success('保存成功');
    fetchStatus(); // Refresh status as changing config might restart scheduler
  } catch (e) {
    toast.error('保存失败');
  } finally {
    savingCf.value = false;
  }
};
</script>

<style scoped>
.dashboard-redesign {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  margin-bottom: 0.12rem;
}

.workspace-kicker {
  display: inline-flex;
  align-items: center;
  padding: 0.32rem 0.72rem;
  border-radius: 999px;
  background: rgba(var(--primary-rgb), 0.12);
  color: var(--primary-color);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.insight-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(320px, 0.9fr);
  align-items: stretch;
  gap: 1.5rem;
}

.workspace-card,
.config-stage {
  height: 100%;
  border-radius: 1.4rem;
  background: var(--bg-surface);
  border: 1px solid rgba(161, 172, 184, 0.14);
  box-shadow: var(--shadow-sm);
}

.workspace-card {
  padding: 1.6rem 1.5rem 1.5rem;
}

.config-editor-shell {
  padding: 1.5rem;
  border-radius: 1.1rem;
  border: 1px solid rgba(161, 172, 184, 0.16);
  background: rgba(161, 172, 184, 0.06);
}

.workspace-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.workspace-card-header h3,
.config-stage-head h3 {
  margin: 0.2rem 0 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-heading);
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

.workspace-empty {
  min-height: 17rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: var(--text-muted);
}

.workspace-empty i {
  font-size: 2.2rem;
}

.workflow-stack {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.workflow-node {
  display: grid;
  grid-template-columns: 3.25rem minmax(0, 1fr);
  gap: 1rem;
  align-items: stretch;
  padding: 1rem;
  border-radius: 1rem;
  background: rgba(var(--primary-rgb), 0.08);
  border: 1px solid rgba(var(--primary-rgb), 0.14);
}

.workflow-node-marker {
  width: 2.9rem;
  height: 2.9rem;
  border-radius: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--primary-rgb), 0.16);
  color: var(--primary-color);
  font-size: 1.2rem;
}

.workflow-node-body {
  padding: 0;
  border-radius: 0;
  background: transparent;
  border: 0;
}

.workflow-node-top {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.workflow-node-top h4,
.notice-panel h4 {
  margin: 0;
  color: var(--text-heading);
  font-size: 1rem;
  font-weight: 700;
}

.workflow-node-body p {
  margin: 0.5rem 0 0;
  color: rgba(67, 89, 113, 0.78);
  line-height: 1.6;
}

.action-tile-list {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.action-tile {
  display: grid;
  grid-template-columns: 2.9rem minmax(0, 1fr);
  gap: 0.9rem;
  align-items: center;
  padding: 1rem;
  border-radius: 1rem;
  border: 1px solid transparent;
  text-align: left;
  cursor: pointer;
  transition: transform var(--transition-base), box-shadow var(--transition-base), border-color var(--transition-base), background-color var(--transition-base);
}

.action-tile:hover:not(:disabled),
.action-tile:focus-visible:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.action-tile:focus-visible {
  outline: none;
}

.action-tile:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.action-tile i {
  width: 2.9rem;
  height: 2.9rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.9rem;
  font-size: 1.25rem;
}

.action-tile strong {
  display: block;
  margin-bottom: 0.2rem;
  color: inherit;
}

.action-tile span {
  display: block;
  font-size: 0.84rem;
  opacity: 0.82;
}

.action-tile-primary {
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
  border-color: rgba(var(--primary-rgb), 0.16);
}

.action-tile-primary i {
  background: rgba(var(--primary-rgb), 0.16);
}

.action-tile-primary:hover:not(:disabled),
.action-tile-primary:focus-visible:not(:disabled) {
  background: rgba(var(--primary-rgb), 0.14);
  border-color: rgba(var(--primary-rgb), 0.28);
}

.action-tile-success {
  background: rgba(74, 179, 126, 0.1);
  color: var(--success-color);
  border-color: rgba(74, 179, 126, 0.16);
}

.action-tile-success i {
  background: rgba(74, 179, 126, 0.16);
}

.action-tile-success:hover:not(:disabled),
.action-tile-success:focus-visible:not(:disabled) {
  background: rgba(74, 179, 126, 0.14);
  border-color: rgba(74, 179, 126, 0.28);
}

.action-tile-danger {
  background: rgba(225, 108, 108, 0.1);
  color: var(--danger-color);
  border-color: rgba(225, 108, 108, 0.16);
}

.action-tile-danger i {
  background: rgba(225, 108, 108, 0.16);
}

.action-tile-danger:hover:not(:disabled),
.action-tile-danger:focus-visible:not(:disabled) {
  background: rgba(225, 108, 108, 0.14);
  border-color: rgba(225, 108, 108, 0.28);
}

.notice-panel {
  margin-top: 1.25rem;
  padding: 1rem 1.1rem;
  border-radius: 1rem;
  background: rgba(79, 183, 211, 0.08);
  border: 1px solid rgba(79, 183, 211, 0.16);
}

.notice-panel h4 {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  margin-bottom: 0.9rem;
}

.notice-panel ul {
  margin: 0;
  padding-left: 1.15rem;
  color: var(--text-muted);
  line-height: 1.75;
}

.config-stage {
  padding: 1.5rem;
}

.compact-stage {
  padding: 1.6rem 1.25rem 1.25rem;
}

.config-workflow-empty {
  min-height: 10rem;
}

.config-workflow-stack {
  gap: 0.85rem;
  margin-bottom: 1rem;
}

.config-stage-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.config-stage-heading {
  flex: 1 1 auto;
  min-width: 0;
}

.config-stage-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.85rem;
  flex-wrap: nowrap;
}

.config-stage-title-row .workspace-pill {
  flex-shrink: 0;
}

.config-stage-hint {
  color: var(--text-muted);
  font-size: 0.84rem;
}

.config-stage-body {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.toggle-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid rgba(161, 172, 184, 0.14);
}

.toggle-row .switch {
  flex-shrink: 0;
}

.toggle-row p {
  margin: 0.25rem 0 0;
  color: var(--text-muted);
  font-size: 0.86rem;
}

.toggle-row strong {
  color: var(--text-heading);
}

.config-field small {
  display: block;
  margin-top: 0.55rem;
  color: var(--text-muted);
}

.save-config-btn {
  width: auto;
  margin-top: 1rem;
  justify-self: start;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.32rem;
  padding: 0.54rem 0.92rem;
  border: 1px solid transparent;
  border-radius: 0.8rem;
  background: linear-gradient(135deg, rgba(var(--primary-rgb), 0.98), rgba(var(--primary-rgb), 0.82));
  color: #fff;
  font-size: 0.92rem;
  font-weight: 600;
  line-height: 1;
  box-shadow: 0 0.75rem 1.6rem rgba(var(--primary-rgb), 0.24);
  transition: transform var(--transition-base), box-shadow var(--transition-base), filter var(--transition-base), opacity var(--transition-base);
}

.save-config-btn span {
  display: inline-flex;
  align-items: center;
  gap: 0.26rem;
}

.save-config-btn:hover:not(:disabled),
.save-config-btn:focus-visible:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 0.95rem 1.8rem rgba(var(--primary-rgb), 0.28);
  filter: none;
}

.save-config-btn:focus-visible {
  outline: none;
}

.save-config-btn:disabled {
  opacity: 0.72;
  cursor: not-allowed;
  box-shadow: none;
}

.mono-text {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

.workflow-next-run {
  color: var(--text-heading);
  font-weight: 600;
}

.animated-button-primary {
  --btn-color: var(--primary-color);
}

.animated-button-secondary {
  --btn-color: var(--success-color);
}

.animated-button-danger {
  --btn-color: var(--danger-color);
}

@media (max-width: 1199.98px) {
  .insight-grid,
  .config-stage-body {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 767.98px) {
  .workspace-card,
  .config-stage {
    padding: 1rem;
  }

  .workflow-node-marker,
  .action-tile i {
    width: 2.75rem;
    height: 2.75rem;
  }

  .workflow-node {
    grid-template-columns: 2.75rem minmax(0, 1fr);
    gap: 0.8rem;
    align-items: center;
  }

  .action-tile {
    grid-template-columns: 2.75rem minmax(0, 1fr);
    gap: 0.8rem;
    align-items: center;
  }

  .workflow-node {
    grid-template-columns: 2.75rem minmax(0, 1fr);
    gap: 0.7rem;
    align-items: flex-start;
  }

  .workflow-node-top {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.35rem;
  }

  .workflow-node-body {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .workflow-node-top h4,
  .workflow-next-run {
    width: 100%;
  }

  .workflow-next-run {
    font-weight: 400;
  }

  .workflow-node-desc {
    display: none;
  }

  .config-stage-head {
    align-items: flex-start;
  }

  .config-stage-title-row {
    gap: 0.7rem;
  }

  .toggle-row {
    justify-content: space-between;
    align-items: flex-start;
  }

  .toggle-row .switch {
    order: 2;
    margin-right: 0 !important;
    margin-left: 0.75rem;
  }

  .toggle-row > div:last-child {
    order: 1;
    flex: 1 1 auto;
  }

  .config-editor-shell {
    display: flex;
    flex-direction: column;
  }

  .save-config-btn {
    align-self: flex-end;
    justify-self: auto;
    margin-top: 1.25rem;
    margin-left: auto;
  }
}

  .switch {
    --switch-width: 46px;
    --switch-height: 24px;
    --switch-bg: rgba(161, 172, 184, 0.42);
    --switch-checked-bg: linear-gradient(135deg, color-mix(in srgb, var(--success-color) 86%, #3dd598) 0%, var(--success-color) 100%);
    --switch-offset: calc((var(--switch-height) - var(--circle-diameter)) / 2);
    --switch-transition: all .2s cubic-bezier(0.27, 0.2, 0.25, 1.51);
    --circle-diameter: 18px;
    --circle-bg: #fff;
    --circle-shadow: 0 0.125rem 0.5rem rgba(67, 89, 113, 0.24);
    --circle-checked-shadow: 0 0.125rem 0.75rem rgba(74, 179, 126, 0.3);
    --circle-transition: var(--switch-transition);
    --icon-transition: all .2s cubic-bezier(0.27, 0.2, 0.25, 1.51);
    --icon-cross-color: var(--switch-bg);
    --icon-cross-size: 6px;
    --icon-checkmark-color: var(--success-color);
    --icon-checkmark-size: 10px;
    --effect-width: calc(var(--circle-diameter) / 2);
    --effect-height: calc(var(--effect-width) / 2 - 1px);
    --effect-bg: var(--circle-bg);
    --effect-border-radius: 1px;
    --effect-transition: all .2s ease-in-out;
  }

  .switch input {
    display: none;
  }

  .switch {
    display: inline-block;
  }

  .switch svg {
    -webkit-transition: var(--icon-transition);
    -o-transition: var(--icon-transition);
    transition: var(--icon-transition);
    position: absolute;
      top: 50%;
      left: 50%;
    height: auto;
  }

  .switch .checkmark {
    width: var(--icon-checkmark-size);
    color: var(--icon-checkmark-color);
      -webkit-transform: translate(-50%, -50%) scale(0);
      -ms-transform: translate(-50%, -50%) scale(0);
      transform: translate(-50%, -50%) scale(0);
  }

  .switch .cross {
    width: var(--icon-cross-size);
    color: var(--icon-cross-color);
      -webkit-transform: translate(-50%, -50%) scale(1);
      -ms-transform: translate(-50%, -50%) scale(1);
      transform: translate(-50%, -50%) scale(1);
  }

  .slider {
    -webkit-box-sizing: border-box;
    box-sizing: border-box;
    width: var(--switch-width);
    height: var(--switch-height);
    background: var(--switch-bg);
    border-radius: 999px;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    position: relative;
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
    -webkit-transition: var(--switch-transition);
    -o-transition: var(--switch-transition);
    transition: var(--switch-transition);
    cursor: pointer;
  }

  .circle {
    width: var(--circle-diameter);
    height: var(--circle-diameter);
    background: var(--circle-bg);
    border-radius: inherit;
    -webkit-box-shadow: var(--circle-shadow);
    box-shadow: var(--circle-shadow);
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    -webkit-box-pack: center;
    -ms-flex-pack: center;
    justify-content: center;
    -webkit-transition: var(--circle-transition);
    -o-transition: var(--circle-transition);
    transition: var(--circle-transition);
    z-index: 1;
    position: absolute;
      top: 50%;
    left: var(--switch-offset);
      -webkit-transform: translateY(-50%);
      -ms-transform: translateY(-50%);
      transform: translateY(-50%);
  }

  .slider::before {
    content: "";
    position: absolute;
    width: var(--effect-width);
    height: var(--effect-height);
      top: 50%;
    left: calc(var(--switch-offset) + (var(--effect-width) / 2));
    background: var(--effect-bg);
    border-radius: var(--effect-border-radius);
    -webkit-transition: var(--effect-transition);
    -o-transition: var(--effect-transition);
    transition: var(--effect-transition);
      -webkit-transform: translateY(-50%);
      -ms-transform: translateY(-50%);
      transform: translateY(-50%);
  }

  .switch input:checked+.slider {
    background: var(--switch-checked-bg);
  }

  .switch input:checked+.slider .checkmark {
    -webkit-transform: translate(-50%, -50%) scale(1);
    -ms-transform: translate(-50%, -50%) scale(1);
    transform: translate(-50%, -50%) scale(1);
  }

  .switch input:checked+.slider .cross {
    -webkit-transform: translate(-50%, -50%) scale(0);
    -ms-transform: translate(-50%, -50%) scale(0);
    transform: translate(-50%, -50%) scale(0);
  }

  .switch input:checked+.slider::before {
    left: calc(100% - var(--effect-width) - (var(--effect-width) / 2) - var(--switch-offset));
  }

  .switch input:checked+.slider .circle {
    left: calc(100% - var(--circle-diameter) - var(--switch-offset));
    -webkit-box-shadow: var(--circle-checked-shadow);
    box-shadow: var(--circle-checked-shadow);
  }

  .animated-button-primary {
    --btn-color: var(--primary-color);
  }

  .animated-button-secondary {
    --btn-color: var(--success-color);
  }

  .animated-button-danger {
    --btn-color: var(--danger-color);
  }
</style>
