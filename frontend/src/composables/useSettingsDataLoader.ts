import { computed, type Ref } from 'vue';
import { backup, cfst, ikuai, notify, scheduler, settings } from '@/api';
import { getErrorMessage } from '@/utils/error';
import { normalizeNotifyType, pickNotifyConfig } from '@/utils/notify';
import type { CfstConfig, CfstResult } from '@/api/cfst';
import type { IkuaiStatus } from '@/api/ikuai';
import type { NotifyChannelConfig } from '@/api/notify';
import type { SchedulerJob } from '@/api/scheduler';
import type {
  AuthFormState,
  BackupFormState,
  CfstFormState,
  CfstResultItem,
  CfstStatusState,
  IkuaiDnsFormState,
  NotifyChannel,
  NotifyChannelPayload,
  PageOverviewCard,
  SettingPageKey,
} from '@/types/settings';

interface UseSettingsDataLoaderOptions {
  authInitialized: Ref<boolean>;
  authForm: AuthFormState;
  backupForm: BackupFormState;
  cfstForm: CfstFormState;
  cfstStatus: Ref<CfstStatusState>;
  cfstResults: Ref<CfstResultItem[]>;
  cfstBestIp: Ref<string>;
  cfstResultFile: Ref<string>;
  cfstLastUpdated: Ref<string>;
  runningCfst: Ref<boolean>;
  loadingCfstResults: Ref<boolean>;
  cfstPollingTimer: Ref<number | null>;
  ikuaiDnsForm: IkuaiDnsFormState;
  notifyChannels: Ref<NotifyChannel[]>;
  hasLoadedSystemPage: Ref<boolean>;
  hasLoadedNotifyPage: Ref<boolean>;
  hasLoadedBackupPage: Ref<boolean>;
  hasLoadedCfstPage: Ref<boolean>;
  hasLoadedIkuaiPage: Ref<boolean>;
  activePage: Ref<SettingPageKey>;
  toast: { error: (message: string) => void };
  getCfstNumberValue: (value: unknown, fallback: number) => number;
  toCfstDisplayValue: (value: unknown, fallback: number) => number | null;
  toCfstDisplayText: (value: unknown, fallback: string) => string;
  cfstDefaults: {
    threads: number;
    ping_times: number;
    download_count: number;
    download_time: number;
    timeout_seconds: number;
    tcp_port: number;
    url: string;
    min_delay: number;
    max_delay: number;
    max_loss_rate: number;
    min_speed: number;
    show_count: number;
  };
}

interface SettingsConfigAuth {
  username?: string;
}

interface SettingsConfigPayload {
  auth?: SettingsConfigAuth;
}

interface BackupConfigPayload {
  webdav_enabled?: boolean;
  webdav_url?: string;
  webdav_path?: string;
  webdav_username?: string;
  webdav_password?: string;
  local_keep_count?: number;
}

const getCfstTimeoutValue = (config: Partial<CfstConfig> & { timeout_seconds?: number }) => {
  return config.timeout_seconds ?? 300;
};

const getIkuaiPasswordValue = (status: IkuaiStatus & { password?: string }) => {
  return status.password || '';
};

const normalizeCfstResult = (item: CfstResult): CfstResultItem => ({
  ...item,
  sent: item.sent ?? undefined,
  received: item.received ?? undefined,
  loss_rate: item.loss_rate ?? undefined,
  avg_latency: item.avg_latency ?? undefined,
  download_speed: item.download_speed ?? undefined,
});

const normalizeNotifyChannel = (channel: NotifyChannelConfig): NotifyChannel => {
  const rawChannel = channel as unknown as Record<string, unknown>;
  const config = (channel.config as Record<string, unknown> | undefined) || {};

  return {
    ...rawChannel,
    ...config,
    id: String(channel.id || ''),
    name: String(channel.name || ''),
    type: normalizeNotifyType(String(channel.type || '')),
    enabled: channel.enabled !== undefined ? Boolean(channel.enabled) : true,
    config,
    HITOKOTO: Boolean(config.HITOKOTO),
  } as NotifyChannel;
};

const toNotifyPayload = (channelData: NotifyChannel): NotifyChannelPayload => {
  const {
    id: _id,
    name,
    type,
    enabled,
    config: _config,
    ...rest
  } = channelData;

  return {
    name,
    type: normalizeNotifyType(type),
    enabled: Boolean(enabled),
    config: pickNotifyConfig(type, rest),
  };
};

const buildCfstOverviewCards = (
  cfstForm: CfstFormState,
  cfstDefaults: UseSettingsDataLoaderOptions['cfstDefaults']
): PageOverviewCard[] => [
  {
    label: '延迟线程',
    value: String(cfstForm.threads ?? cfstDefaults.threads),
    description: '对应 -n，决定延迟测速的并发规模。',
  },
  {
    label: '延迟阈值',
    value: `${cfstForm.max_delay ?? cfstDefaults.max_delay} ms`,
    description: '超过该平均延迟的候选 IP 会被过滤。',
  },
  {
    label: '展示数量',
    value: `${cfstForm.show_count ?? cfstDefaults.show_count} 条`,
    description: '测速完成后展示的结果数量。',
  },
];

export const useSettingsDataLoader = ({
  authInitialized,
  authForm,
  backupForm,
  cfstForm,
  cfstStatus,
  cfstResults,
  cfstBestIp,
  cfstResultFile,
  cfstLastUpdated,
  runningCfst,
  loadingCfstResults,
  cfstPollingTimer,
  ikuaiDnsForm,
  notifyChannels,
  hasLoadedSystemPage,
  hasLoadedNotifyPage,
  hasLoadedBackupPage,
  hasLoadedCfstPage,
  hasLoadedIkuaiPage,
  activePage,
  toast,
  getCfstNumberValue,
  toCfstDisplayValue,
  toCfstDisplayText,
  cfstDefaults,
}: UseSettingsDataLoaderOptions) => {
  const cfstOverviewCards = computed(() => buildCfstOverviewCards(cfstForm, cfstDefaults));

  const stopCfstPolling = () => {
    if (cfstPollingTimer.value !== null) {
      window.clearInterval(cfstPollingTimer.value);
      cfstPollingTimer.value = null;
    }
  };

  const fetchNotifyChannels = async () => {
    const response = await notify.listChannels();
    notifyChannels.value = (response.data?.channels || []).map(normalizeNotifyChannel);
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
    } catch (e: any) {
      if (!silent) {
        toast.error('获取测速结果失败: ' + getErrorMessage(e, '请求失败，请稍后重试'));
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
    } catch (e: any) {
      stopCfstPolling();
      runningCfst.value = false;
      if (!silent) {
        toast.error('获取测速状态失败: ' + getErrorMessage(e, '请求失败，请稍后重试'));
      }
    }
  };

  const fetchAuthSettings = async () => {
    const [settingsResponse, systemInfoResponse] = await Promise.all([
      settings.config(),
      settings.info()
    ]);

    const data = (settingsResponse.data || {}) as SettingsConfigPayload;
    const systemInfo = systemInfoResponse.data || {};
    const auth = data.auth || {};

    authInitialized.value = Boolean(systemInfo.initialized);
    authForm.username = auth.username || 'admin';
  };

  const fetchBackupSettings = async () => {
    const [backupResponse, backupJobResponse] = await Promise.all([
      backup.getConfig(),
      scheduler.getJob('backup').catch(() => null)
    ]);

    const backupData = (backupResponse.data || {}) as BackupConfigPayload;
    const backupJobData: Partial<SchedulerJob> | null = backupJobResponse?.data ?? null;
    const hasBackupJob = Boolean(backupJobData?.job_id);

    backupForm.enable = hasBackupJob ? Boolean(backupJobData?.enabled) : Boolean(backupData.webdav_enabled);
    backupForm.webdav_url = backupData.webdav_url || '';
    backupForm.webdav_path = backupData.webdav_path || '/PT-Accelerator';
    backupForm.webdav_username = backupData.webdav_username || '';
    backupForm.webdav_password = backupData.webdav_password || '';
    backupForm.cron = backupJobData?.cron_expr || '0 2 * * *';
    backupForm.backup_count = backupData.local_keep_count ?? 5;
  };

  const fetchCfstSettings = async () => {
    const cfstResponse = await cfst.getConfig();
    const cfstData = (cfstResponse.data || {}) as Partial<CfstConfig> & { timeout_seconds?: number };

    cfstForm.threads = toCfstDisplayValue(cfstData.threads, cfstDefaults.threads);
    cfstForm.ping_times = toCfstDisplayValue(cfstData.ping_times, cfstDefaults.ping_times);
    cfstForm.download_count = getCfstNumberValue(cfstData.download_count, cfstDefaults.download_count);
    cfstForm.download_time = toCfstDisplayValue(cfstData.download_time, cfstDefaults.download_time);
    cfstForm.timeout_seconds = toCfstDisplayValue(getCfstTimeoutValue(cfstData), cfstDefaults.timeout_seconds);
    cfstForm.tcp_port = toCfstDisplayValue(cfstData.tcp_port, cfstDefaults.tcp_port);
    cfstForm.url = toCfstDisplayText(cfstData.url, cfstDefaults.url);
    cfstForm.httping = Boolean(cfstData.httping);
    cfstForm.httping_code = cfstData.httping_code || '';
    cfstForm.cfcolo = cfstData.cfcolo || '';
    cfstForm.min_delay = toCfstDisplayValue(cfstData.min_delay, cfstDefaults.min_delay);
    cfstForm.max_delay = getCfstNumberValue(cfstData.max_delay, cfstDefaults.max_delay);
    cfstForm.max_loss_rate = toCfstDisplayValue(cfstData.max_loss_rate, cfstDefaults.max_loss_rate);
    cfstForm.min_speed = toCfstDisplayValue(cfstData.min_speed, cfstDefaults.min_speed);
    cfstForm.show_count = toCfstDisplayValue(cfstData.show_count, cfstDefaults.show_count);
    cfstForm.test_all = Boolean(cfstData.test_all);
    cfstForm.disable_download = Boolean(cfstData.disable_download);
    cfstForm.debug = Boolean(cfstData.debug);
    cfstForm.additional_args = cfstData.additional_args || '';
  };

  const fetchIkuaiSettings = async () => {
    const ikuaiResponse = await ikuai.getStatus();
    const ikuaiData = (ikuaiResponse.data || {}) as IkuaiStatus & { password?: string };

    ikuaiDnsForm.enable = Boolean(ikuaiData.enabled);
    ikuaiDnsForm.url = ikuaiData.host || '';
    ikuaiDnsForm.username = ikuaiData.username || 'admin';
    ikuaiDnsForm.password = getIkuaiPasswordValue(ikuaiData);
  };

  const markPageDataStale = (section: SettingPageKey) => {
    switch (section) {
      case 'system':
        hasLoadedSystemPage.value = false;
        break;
      case 'notification':
        hasLoadedNotifyPage.value = false;
        break;
      case 'backup':
        hasLoadedBackupPage.value = false;
        break;
      case 'cfst':
        hasLoadedCfstPage.value = false;
        break;
      case 'ikuai-dns':
        hasLoadedIkuaiPage.value = false;
        break;
    }
  };

  const ensurePageDataReady = async (section: SettingPageKey) => {
    switch (section) {
      case 'system':
        if (!hasLoadedSystemPage.value) {
          await fetchAuthSettings();
          hasLoadedSystemPage.value = true;
        }
        break;
      case 'notification':
        if (!hasLoadedNotifyPage.value) {
          await fetchNotifyChannels();
          hasLoadedNotifyPage.value = true;
        }
        break;
      case 'backup':
        if (!hasLoadedBackupPage.value) {
          await fetchBackupSettings();
          hasLoadedBackupPage.value = true;
        }
        break;
      case 'cfst':
        if (!hasLoadedCfstPage.value) {
          await fetchCfstSettings();
          await fetchCfstStatus(true);
          await fetchCfstResults(true);
          hasLoadedCfstPage.value = true;
        }
        break;
      case 'ikuai-dns':
        if (!hasLoadedIkuaiPage.value) {
          await fetchIkuaiSettings();
          hasLoadedIkuaiPage.value = true;
        }
        break;
    }
  };

  const fetchCurrentSectionSettings = async () => {
    await ensurePageDataReady(activePage.value);
  };

  const activePageLoaded = computed(() => {
    switch (activePage.value) {
      case 'system':
        return hasLoadedSystemPage.value;
      case 'notification':
        return hasLoadedNotifyPage.value;
      case 'backup':
        return hasLoadedBackupPage.value;
      case 'cfst':
        return hasLoadedCfstPage.value;
      case 'ikuai-dns':
        return hasLoadedIkuaiPage.value;
      default:
        return false;
    }
  });

  return {
    cfstOverviewCards,
    activePageLoaded,
    fetchCurrentSectionSettings,
    fetchCfstResults,
    fetchCfstStatus,
    markPageDataStale,
    ensurePageDataReady,
    toNotifyPayload,
    stopCfstPolling,
  };
};
