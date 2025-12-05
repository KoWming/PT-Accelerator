<template>
  <div>
    <div class="page-header">
      <div>
        <h2 class="page-title">控制面板</h2>
      </div>
      <div class="d-flex align-items-center">
        <!-- Badge moved to card header, so this is empty or can be removed if not needed -->
      </div>
    </div>
    
    <div class="row g-4">
      <!-- Status Card -->
      <div class="col-lg-8">
        <div class="card h-100 shadow-sm">
          <div class="card-header bg-transparent border-0 pt-4 px-4 pb-0 d-flex justify-content-between align-items-center">
            <h5 class="mb-0 fw-bold"><i class="bi bi-clock-history me-2 text-primary"></i>调度器状态</h5>
            <span class="badge rounded-pill px-3 py-2" :class="schedulerRunning ? 'bg-success bg-opacity-10 text-success' : 'bg-danger bg-opacity-10 text-danger'">
              <i class="bi me-1" :class="schedulerRunning ? 'bi-check-circle-fill' : 'bi-x-circle-fill'"></i>
              {{ schedulerRunning ? '运行中' : '已停止' }}
            </span>
          </div>
          <div class="card-body p-4">
            <div v-if="jobs.length === 0" class="text-center py-5 text-muted">
              <i class="bi bi-inbox fs-1 d-block mb-3 opacity-50"></i>
              暂无任务
            </div>
            <div v-else class="list-group list-group-flush">
              <div class="list-group-item bg-transparent px-0 py-3 d-flex align-items-start" v-for="job in jobs" :key="job.name">
                <div class="icon-square bg-primary bg-opacity-10 text-primary me-3 rounded-3 d-flex align-items-center justify-content-center flex-shrink-0" style="width: 40px; height: 40px;">
                  <i class="bi bi-calendar-check"></i>
                </div>
                <div class="flex-grow-1">
                  <h6 class="mb-0 fw-semibold">{{ job.name }}</h6>
                  <div class="d-flex justify-content-between align-items-baseline mt-1">
                    <small class="text-muted">下次运行</small>
                    <span class="text-muted font-monospace">{{ job.next_run }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="col-lg-4">
        <div class="card h-100 shadow-sm">
          <div class="card-header bg-transparent border-0 pt-4 px-4 pb-0">
            <h5 class="mb-0 fw-bold"><i class="bi bi-lightning me-2 text-warning"></i>快捷操作</h5>
          </div>
          <div class="card-body p-4 d-flex flex-column gap-3">
            <button class="animated-button animated-button-primary w-100 py-3 shadow-sm" @click="runCloudflareTest" :disabled="runningCf">
              <span class="btn-content">
                <span v-if="runningCf" class="spinner-border spinner-border-sm"></span>
                <i v-else class="bi bi-play-circle-fill"></i>
                <span class="ms-2">运行IP优选与Hosts更新</span>
              </span>
              <span class="btn-ripple"></span>
            </button>
            
            <button class="animated-button animated-button-secondary w-100 py-3 shadow-sm" @click="updateHosts" :disabled="updatingHosts">
              <span class="btn-content">
                <span v-if="updatingHosts" class="spinner-border spinner-border-sm"></span>
                <i v-else class="bi bi-arrow-clockwise"></i>
                <span class="ms-2">仅更新Hosts</span>
              </span>
              <span class="btn-ripple"></span>
            </button>

            <button class="animated-button animated-button-danger w-100 py-3 shadow-sm" @click="handleClearAndUpdate" :disabled="clearing">
              <span class="btn-content">
                <span v-if="clearing" class="spinner-border spinner-border-sm"></span>
                <i v-else class="bi bi-trash-fill"></i>
                <span class="ms-2">清空Hosts文件并更新Hosts</span>
              </span>
              <span class="btn-ripple"></span>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Scheduled Task Configuration -->
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-header bg-transparent border-0 pt-4 px-4 pb-0">
            <h5 class="mb-0 fw-bold"><i class="bi bi-gear me-2 text-secondary"></i>定时任务配置</h5>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="saveCloudflareSettings">
              <div class="row g-4">
                <div class="col-md-6">
                  <div class="d-flex align-items-center mb-3">
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
                    <span class="fw-bold">启用定时任务</span>
                  </div>
                  
                  <div class="mb-3" ref="cronInputRef">
                    <label class="form-label text-muted small">CRON表达式</label>
                    <CronInput v-model="cfConfig.cron" @edit="showCronEditor = true" />
                  </div>
                  
                  <p class="text-muted small mb-3">默认值: 0 0 * * * (每天零点执行IP优选与Hosts更新)</p>
                  
                  <button type="submit" class="save-config-btn w-100" :disabled="savingCf">
                    <span>
                      <span v-if="savingCf" class="spinner-border spinner-border-sm me-2"></span>
                      <i v-else class="bi bi-save me-2"></i>
                      保存配置
                    </span>
                  </button>
                </div>
                
                <div class="col-md-6">
                  <div v-if="!showCronEditor" class="alert alert-info border-0 bg-info bg-opacity-10 h-100 mb-0" style="color: #16b1ff">
                    <div class="d-flex align-items-center gap-2 mb-2">
                      <i class="bi bi-info-circle-fill"></i>
                      <h6 class="fw-bold mb-0">CRON表达式说明:</h6>
                    </div>
                    <div class="ps-4">
                      <p class="mb-1 font-monospace" style="color: #16b1ff">分 时 日 月 周</p>
                      <ul class="list-unstyled mb-0 font-monospace small" style="color: #16b1ff">
                        <li>0 0 * * * = 每天 00:00 执行</li>
                        <li>0 */6 * * * = 每6小时执行一次</li>
                        <li>0 0 * * 0 = 每周日 00:00 执行</li>
                        <li>0 9-18 * * * = 每天9-18点整点执行</li>
                        <li>*/30 * * * * = 每30分钟执行一次</li>
                        <li>0 2 1 * * = 每月1日 02:00 执行</li>
                      </ul>
                    </div>
                  </div>
                  <div 
                    v-else 
                    class="h-100"
                    ref="cronEditorRef"
                  >
                    <CronEditor 
                      v-model="cfConfig.cron" 
                      @close="showCronEditor = false" 
                    />
                  </div>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive } from 'vue';
import axios from '../../api/axios';
import { useTrackerStore } from '../../stores/trackers';
import { useHostsStore } from '../../stores/hosts';
import CronInput from '../../components/CronInput.vue';
import CronEditor from '../../components/CronEditor.vue';
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
const showCronEditor = ref(false);
const cronInputRef = ref<HTMLElement | null>(null);
const cronEditorRef = ref<HTMLElement | null>(null);

const cfConfig = reactive({
  enable: true,
  cron: '0 0 * * *'
});

const handleClickOutside = (event: MouseEvent) => {
  if (showCronEditor.value) {
    const target = event.target as Node;
    const isInput = cronInputRef.value && cronInputRef.value.contains(target);
    const isEditor = cronEditorRef.value && cronEditorRef.value.contains(target);
    
    if (!isInput && !isEditor) {
      showCronEditor.value = false;
    }
  }
};

onMounted(async () => {
  document.addEventListener('click', handleClickOutside);
  await fetchStatus();
  await trackerStore.fetchConfig();
  cfConfig.enable = trackerStore.cloudflare.enable;
  cfConfig.cron = trackerStore.cloudflare.cron;
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

const fetchStatus = async () => {
  try {
    const response = await axios.get('/scheduler-status');
    schedulerRunning.value = response.data.running;
    jobs.value = response.data.jobs || [];
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
.action-btn {
  transition: all 0.3s ease;
  border: 1px solid var(--glass-border);
  background: var(--bg-surface);
  color: var(--text-main);
}

.action-btn:hover {
  transform: translateY(-2px);
  background: rgba(var(--text-main), 0.05);
  border-color: var(--primary-color);
  box-shadow: var(--shadow-md);
}

.action-btn:hover .icon-square {
  transform: scale(1.1);
}

.icon-square {
  transition: transform 0.3s ease;
}

  .switch {
    /* switch */
    --switch-width: 46px;
    --switch-height: 24px;
    --switch-bg: rgb(131, 131, 131);
    --switch-checked-bg: rgb(0, 218, 80);
    --switch-offset: calc((var(--switch-height) - var(--circle-diameter)) / 2);
    --switch-transition: all .2s cubic-bezier(0.27, 0.2, 0.25, 1.51);
    /* circle */
    --circle-diameter: 18px;
    --circle-bg: #fff;
    --circle-shadow: 1px 1px 2px rgba(146, 146, 146, 0.45);
    --circle-checked-shadow: -1px 1px 2px rgba(163, 163, 163, 0.45);
    --circle-transition: var(--switch-transition);
    /* icon */
    --icon-transition: all .2s cubic-bezier(0.27, 0.2, 0.25, 1.51);
    --icon-cross-color: var(--switch-bg);
    --icon-cross-size: 6px;
    --icon-checkmark-color: var(--switch-checked-bg);
    --icon-checkmark-size: 10px;
    /* effect line */
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
    height: auto;
  }

  .switch .checkmark {
    width: var(--icon-checkmark-size);
    color: var(--icon-checkmark-color);
    -webkit-transform: scale(0);
    -ms-transform: scale(0);
    transform: scale(0);
  }

  .switch .cross {
    width: var(--icon-cross-size);
    color: var(--icon-cross-color);
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
    left: var(--switch-offset);
  }

  .slider::before {
    content: "";
    position: absolute;
    width: var(--effect-width);
    height: var(--effect-height);
    left: calc(var(--switch-offset) + (var(--effect-width) / 2));
    background: var(--effect-bg);
    border-radius: var(--effect-border-radius);
    -webkit-transition: var(--effect-transition);
    -o-transition: var(--effect-transition);
    transition: var(--effect-transition);
  }

  /* actions */

  .switch input:checked+.slider {
    background: var(--switch-checked-bg);
  }

  .switch input:checked+.slider .checkmark {
    -webkit-transform: scale(1);
    -ms-transform: scale(1);
    transform: scale(1);
  }

  .switch input:checked+.slider .cross {
    -webkit-transform: scale(0);
    -ms-transform: scale(0);
    transform: scale(0);
  }

  .switch input:checked+.slider::before {
    left: calc(100% - var(--effect-width) - (var(--effect-width) / 2) - var(--switch-offset));
  }

  .switch input:checked+.slider .circle {
    left: calc(100% - var(--circle-diameter) - var(--switch-offset));
    -webkit-box-shadow: var(--circle-checked-shadow);
    box-shadow: var(--circle-checked-shadow);
  }

  /* Animated Button Styles */
  .animated-button {
    position: relative;
    display: inline-block;
    padding: 12px 24px;
    border: 1px solid transparent;
    font-size: 16px;
    background-color: color-mix(in srgb, var(--btn-color), transparent 90%);
    border-radius: 0.5rem;
    font-weight: 600;
    color: var(--btn-color);
    cursor: pointer;
    overflow: hidden;
    transition: all 0.6s cubic-bezier(0.23, 1, 0.320, 1);
    
    /* Default color fallback */
    --btn-color: #2196F3;
  }

  .animated-button-primary {
    --btn-color: var(--primary-color);
  }

  .animated-button-secondary {
    --btn-color: var(--secondary-color);
  }

  .animated-button-danger {
    --btn-color: var(--danger-color);
  }

  .btn-ripple {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 20px;
    height: 20px;
    background-color: var(--btn-color);
    border-radius: 50%;
    opacity: 0;
    transition: all 0.8s cubic-bezier(0.23, 1, 0.320, 1);
    z-index: 0;
  }

  .btn-content {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    white-space: nowrap;
    transition: color 0.6s cubic-bezier(0.23, 1, 0.320, 1);
  }

  .animated-button:hover {
    color: #ffffff;
    border-color: transparent;
  }

  .animated-button:active {
    scale: 0.95;
  }

  .animated-button:hover .btn-ripple {
    width: 150%;
    height: 500%; /* Make sure it covers the whole button */
    opacity: 1;
  }
  
  /* Disabled state */
  .animated-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
  }

  /* Save Config Button */
  .save-config-btn {
    border: 2px solid #24b4fb;
    background-color: #24b4fb;
    border-radius: 0.9em;
    cursor: pointer;
    padding: 0.8em 1.2em 0.8em 1em;
    transition: all ease-in-out 0.2s;
    font-size: 16px;
    color: #fff;
  }

  .save-config-btn span {
    display: flex;
    justify-content: center;
    align-items: center;
    color: #fff;
    font-weight: 600;
  }

  .save-config-btn:hover {
    background-color: #0071e2;
    border-color: #0071e2;
  }

  .save-config-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    background-color: #7dcfff;
    border-color: #7dcfff;
  }
</style>
