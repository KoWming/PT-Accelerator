<template>
  <SettingsPageShell
    page-title="CFST 设置"
    context-title="Cloudflare IP 优选"
    description=""
    :loaded="hasLoadedCfstPage"
    :refreshing="pageRefreshing"
    :overview-cards="[]"
    :feedback="statusBanner"
    page-class="cfst-page-redesign"
    kicker=""
    :hide-context-panel="true"
    :hide-status-banner="true"
    @refresh="refreshCfstPage"
  >
    <article class="workspace-card settings-auth-card settings-cfst-card">
      <header class="workspace-card-header settings-auth-header">
        <div class="settings-card-heading">
          <div class="settings-card-title-row">
            <h3>CFST 设置</h3>
          </div>
          <p>按 `CloudflareSpeedTest` 项目参数配置延迟测试、下载测速、过滤条件与高级选项。</p>
        </div>
      </header>

      <CfstSettingsFormSection
        :cfst-form="cfstForm"
        :saving-cfst="savingCfst"
        :running-cfst="runningCfst"
        :loading-cfst-results="loadingCfstResults"
        @submit="saveCfstSettings"
        @refresh-results="fetchCfstResults()"
        @run-now="runCfstNow"
        @update-field="updateCfstFormField"
      >
        <CfstRuntimeSection
          :cfst-status="cfstStatus"
          :cfst-best-ip="cfstBestIp"
          :cfst-result-file="cfstResultFile"
          :cfst-last-updated="cfstLastUpdated"
          :cfst-has-error="cfstHasError"
          :cfst-results="cfstResults"
          :displayed-cfst-results="displayedCfstResults"
          :visible-cfst-results="visibleCfstResults"
          :running-cfst="runningCfst"
          :format-cfst-date-time="formatCfstDateTime"
          :format-metric="formatMetric"
        />
      </CfstSettingsFormSection>
    </article>
  </SettingsPageShell>
</template>

<script setup lang="ts">
import '@/assets/styles/settings.css';
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue';
import { useToast } from '@/composables/useToast';
import { cfst } from '@/api';
import type { CfstConfig, CfstResult } from '@/api/cfst';
import CfstSettingsFormSection from '@/components/settings/cfst/CfstSettingsFormSection.vue';
import CfstRuntimeSection from '@/components/settings/cfst/CfstRuntimeSection.vue';
import SettingsPageShell from '@/components/settings/shared/SettingsPageShell.vue';
import { useSettingsCfstActions } from '@/composables/useSettingsCfstActions';
import { formatDateTime, formatMetric } from '@/utils/format';
import type {
  CfstFormState,
  CfstResultItem,
  CfstStatusState,
  PageFeedback,
  SettingPageKey,
} from '@/types/settings';

const CFST_DEFAULTS = {
  threads: 200,
  ping_times: 4,
  download_count: 20,
  download_time: 10,
  timeout_seconds: 300,
  tcp_port: 443,
  url: 'https://cf.xiu2.xyz/url',
  min_delay: 0,
  max_delay: 200,
  max_loss_rate: 1,
  min_speed: 0,
  show_count: 10,
};

const getCfstNumberValue = (value: unknown, fallback: number) => {
  if (value === '' || value === null || value === undefined) {
    return fallback;
  }

  const num = Number(value);
  return Number.isNaN(num) ? fallback : num;
};

const getCfstStringValue = (value: unknown, fallback = '') => {
  const normalized = typeof value === 'string' ? value.trim() : '';
  return normalized || fallback;
};

const toCfstDisplayValue = (value: unknown, fallback: number) => {
  const normalized = getCfstNumberValue(value, fallback);
  return normalized === fallback ? null : normalized;
};

const toCfstDisplayText = (value: unknown, fallback: string) => {
  const normalized = typeof value === 'string' ? value.trim() : '';
  return !normalized || normalized === fallback ? '' : normalized;
};

const normalizeCfstResult = (item: CfstResult): CfstResultItem => ({
  ...item,
  sent: item.sent ?? undefined,
  received: item.received ?? undefined,
  loss_rate: item.loss_rate ?? undefined,
  avg_latency: item.avg_latency ?? undefined,
  download_speed: item.download_speed ?? undefined,
});

const getCfstTimeoutValue = (config: Partial<CfstConfig> & { timeout_seconds?: number }) => {
  return config.timeout_seconds ?? 300;
};

const cfstForm = reactive<CfstFormState>({
  threads: null,
  ping_times: null,
  download_count: 20,
  download_time: null,
  timeout_seconds: null,
  tcp_port: null,
  url: '',
  httping: false,
  httping_code: '',
  cfcolo: '',
  min_delay: null,
  max_delay: 200,
  max_loss_rate: null,
  min_speed: null,
  show_count: null,
  test_all: false,
  disable_download: false,
  debug: false,
  additional_args: '',
});

const cfstStatus = ref<CfstStatusState>({
  running: false,
  task_id: null,
  progress: 0,
  result_count: 0,
  message: '空闲',
  started_at: null,
});
const cfstResults = ref<CfstResultItem[]>([]);
const cfstBestIp = ref('');
const cfstResultFile = ref('');
const cfstLastUpdated = ref('');
const cfstPollingTimer = ref<number | null>(null);
const hasLoadedCfstPage = ref(false);
const pageRefreshing = ref(false);
const savingCfst = ref(false);
const runningCfst = ref(false);
const loadingCfstResults = ref(false);
const toast = useToast();
const statusBanner = ref<PageFeedback>({
  title: '',
  message: '',
  status: 'success',
});

const setStatusBanner = (title: string, message: string, status: PageFeedback['status'] = 'success') => {
  statusBanner.value = { title, message, status };
};

const stopCfstPolling = () => {
  if (cfstPollingTimer.value !== null) {
    window.clearInterval(cfstPollingTimer.value);
    cfstPollingTimer.value = null;
  }
};

const fetchCfstResults = async (silent = false) => {
  if (!silent) {
    loadingCfstResults.value = true;
  }

  try {
    const response = await cfst.getResults();
    const data = response.data || {};
    cfstResults.value = Array.isArray(data.results) ? data.results.map(normalizeCfstResult) : [];
    cfstBestIp.value = data.best_ip || '';
    cfstResultFile.value = data.result_file ? './' + data.result_file.split(/[\\/]/).slice(-2).join('/') : '';
    cfstLastUpdated.value = new Date().toISOString();
  } catch (error: any) {
    if (!silent) {
      toast.error('获取测速结果失败: ' + (error.response?.data?.detail || error.message));
    }
  } finally {
    if (!silent) {
      loadingCfstResults.value = false;
    }
  }
};

const fetchCfstStatus = async (silent = true) => {
  try {
    const response = await cfst.getStatus();
    const data = response.data || {};
    cfstStatus.value = {
      running: Boolean(data.running),
      task_id: data.task_id || null,
      progress: Number(data.progress ?? 0),
      result_count: Number(data.result_count ?? 0),
      message: data.message || (data.running ? '测速中' : '空闲'),
      started_at: data.started_at || null,
    };

    runningCfst.value = Boolean(cfstStatus.value.running);

    if (cfstStatus.value.running) {
      if (cfstPollingTimer.value === null) {
        cfstPollingTimer.value = window.setInterval(async () => {
          await fetchCfstStatus(true);
        }, 2000);
      }
      return;
    }

    stopCfstPolling();
    await fetchCfstResults(true);
  } catch (error: any) {
    stopCfstPolling();
    runningCfst.value = false;
    if (!silent) {
      toast.error('获取测速状态失败: ' + (error.response?.data?.detail || error.message));
    }
  }
};

const fetchCfstSettings = async () => {
  const response = await cfst.getConfig();
  const data = (response.data || {}) as Partial<CfstConfig> & { timeout_seconds?: number };

  cfstForm.threads = toCfstDisplayValue(data.threads, CFST_DEFAULTS.threads);
  cfstForm.ping_times = toCfstDisplayValue(data.ping_times, CFST_DEFAULTS.ping_times);
  cfstForm.download_count = getCfstNumberValue(data.download_count, CFST_DEFAULTS.download_count);
  cfstForm.download_time = toCfstDisplayValue(data.download_time, CFST_DEFAULTS.download_time);
  cfstForm.timeout_seconds = toCfstDisplayValue(getCfstTimeoutValue(data), CFST_DEFAULTS.timeout_seconds);
  cfstForm.tcp_port = toCfstDisplayValue(data.tcp_port, CFST_DEFAULTS.tcp_port);
  cfstForm.url = toCfstDisplayText(data.url, CFST_DEFAULTS.url);
  cfstForm.httping = Boolean(data.httping);
  cfstForm.httping_code = data.httping_code || '';
  cfstForm.cfcolo = data.cfcolo || '';
  cfstForm.min_delay = toCfstDisplayValue(data.min_delay, CFST_DEFAULTS.min_delay);
  cfstForm.max_delay = getCfstNumberValue(data.max_delay, CFST_DEFAULTS.max_delay);
  cfstForm.max_loss_rate = toCfstDisplayValue(data.max_loss_rate, CFST_DEFAULTS.max_loss_rate);
  cfstForm.min_speed = toCfstDisplayValue(data.min_speed, CFST_DEFAULTS.min_speed);
  cfstForm.show_count = toCfstDisplayValue(data.show_count, CFST_DEFAULTS.show_count);
  cfstForm.test_all = Boolean(data.test_all);
  cfstForm.disable_download = Boolean(data.disable_download);
  cfstForm.debug = Boolean(data.debug);
  cfstForm.additional_args = data.additional_args || '';
};

const ensureCfstPageReady = async (_section: SettingPageKey) => {
  if (!hasLoadedCfstPage.value) {
    await fetchCfstSettings();
    await fetchCfstStatus(true);
    await fetchCfstResults(true);
    hasLoadedCfstPage.value = true;
  }
};

const markCfstPageStale = (_section: SettingPageKey) => {
  hasLoadedCfstPage.value = false;
};



const visibleCfstResults = computed(() => {
  const showCount = Math.max(getCfstNumberValue(cfstForm.show_count, CFST_DEFAULTS.show_count), 0);

  if (cfstForm.disable_download) {
    const ipResults = cfstResults.value.filter((item) => item?.error || item?.ip);
    return showCount > 0 ? ipResults.slice(0, showCount) : [];
  }

  return cfstResults.value.filter((item) => item?.error || Number(item?.download_speed) > 0);
});

const cfstHasError = computed(() => cfstResults.value.some((item) => Boolean(item?.error)));
const displayedCfstResults = computed(() => {
  if (visibleCfstResults.value.length > 0) {
    return visibleCfstResults.value;
  }

  if (!cfstHasError.value && cfstResults.value.length > 0) {
    return cfstResults.value;
  }

  return [];
});

const {
  saveCfstSettings,
  runCfstNow,
} = useSettingsCfstActions({
  cfstForm,
  savingCfst,
  runningCfst,
  cfstStatus,
  cfstResults,
  cfstBestIp,
  cfstResultFile,
  cfstLastUpdated,
  toast,
  ensurePageDataReady: ensureCfstPageReady,
  markPageDataStale: markCfstPageStale,
  fetchCfstStatus,
  setPageStatusBanner: setStatusBanner,
  getCfstNumberValue,
  getCfstStringValue,
  cfstDefaults: CFST_DEFAULTS,
});

const updateCfstFormField = <K extends keyof CfstFormState>(field: K, value: CfstFormState[K]) => {
  cfstForm[field] = value;
};

const refreshCfstPage = async () => {
  pageRefreshing.value = true;
  try {
    markCfstPageStale('cfst');
    await ensureCfstPageReady('cfst');
    setStatusBanner('CFST 页面已刷新', '当前测速参数、状态与结果已按最新后端状态重新加载。');
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '刷新失败';
    setStatusBanner('CFST 页面刷新失败', message, 'error');
    toast.error(`CFST 页面刷新失败: ${message}`);
  } finally {
    pageRefreshing.value = false;
  }
};

const formatCfstDateTime = (value: string | null) => formatDateTime(value);

onMounted(async () => {
  await ensureCfstPageReady('cfst');
});

onUnmounted(() => {
  stopCfstPolling();
});
</script>

