import type { Ref } from 'vue';
import { useSettingsAuthActions } from '@/composables/useSettingsAuthActions';
import { useSettingsBackupActions } from '@/composables/useSettingsBackupActions';
import { useSettingsCfstActions } from '@/composables/useSettingsCfstActions';
import { useSettingsIkuaiActions } from '@/composables/useSettingsIkuaiActions';
import { useSettingsNotifyActions } from '@/composables/useSettingsNotifyActions';
import type {
  AuthFormState,
  BackupFormState,
  BackupItem,
  CfstFormState,
  CfstResultItem,
  CfstStatusState,
  IkuaiDnsFormState,
  NotifyChannel,
  NotifyChannelPayload,
  PageFeedback,
  SettingPageKey,
} from '@/types/settings';

interface UseSettingsActionsOptions {
  authInitialized: Ref<boolean>;
  authForm: AuthFormState;
  backupForm: BackupFormState;
  cfstForm: CfstFormState;
  ikuaiDnsForm: IkuaiDnsFormState;
  notifyChannels: Ref<NotifyChannel[]>;
  backups: Ref<BackupItem[]>;
  showNotifyModal: Ref<boolean>;
  editingNotifyChannelId: Ref<string | null>;
  editingNotifyChannel: Ref<NotifyChannel | null>;
  testingChannel: Ref<string | null>;
  savingAuth: Ref<boolean>;
  savingBackup: Ref<boolean>;
  savingCfst: Ref<boolean>;
  savingIkuaiDns: Ref<boolean>;
  testingConnection: Ref<boolean>;
  testingIkuaiDns: Ref<boolean>;
  syncingIkuaiDns: Ref<boolean>;
  exportingIkuaiDns: Ref<boolean>;
  importingIkuaiDns: Ref<boolean>;
  runningBackup: Ref<boolean>;
  runningCfst: Ref<boolean>;
  restoringBackup: Ref<boolean>;
  deletingBackupId: Ref<string | null>;
  showBackupModal: Ref<boolean>;
  loadingBackups: Ref<boolean>;
  cfstStatus: Ref<CfstStatusState>;
  cfstResults: Ref<CfstResultItem[]>;
  cfstBestIp: Ref<string>;
  cfstResultFile: Ref<string>;
  cfstLastUpdated: Ref<string>;
  toast: {
    success: (message: string) => void;
    error: (message: string) => void;
    info: (message: string) => void;
  };
  confirm: (message: string, title?: string) => Promise<boolean>;
  ensurePageDataReady: (section: SettingPageKey) => Promise<void>;
  markPageDataStale: (section: SettingPageKey) => void;
  fetchCfstStatus: (silent?: boolean) => Promise<void>;
  toNotifyPayload: (channelData: NotifyChannel) => NotifyChannelPayload;
  setPageStatusBanner: (
    title: string,
    message: string,
    status?: PageFeedback['status']
  ) => void;
  getCfstNumberValue: (value: unknown, fallback: number) => number;
  getCfstStringValue: (value: unknown, fallback?: string) => string;
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

export const useSettingsActions = ({
  authInitialized,
  authForm,
  backupForm,
  cfstForm,
  ikuaiDnsForm,
  notifyChannels,
  backups,
  showNotifyModal,
  editingNotifyChannelId,
  editingNotifyChannel,
  testingChannel,
  savingAuth,
  savingBackup,
  savingCfst,
  savingIkuaiDns,
  testingConnection,
  testingIkuaiDns,
  syncingIkuaiDns,
  exportingIkuaiDns,
  importingIkuaiDns,
  runningBackup,
  runningCfst,
  restoringBackup,
  deletingBackupId,
  showBackupModal,
  loadingBackups,
  cfstStatus,
  cfstResults,
  cfstBestIp,
  cfstResultFile,
  cfstLastUpdated,
  toast,
  confirm,
  ensurePageDataReady,
  markPageDataStale,
  fetchCfstStatus,
  toNotifyPayload,
  setPageStatusBanner,
  getCfstNumberValue,
  getCfstStringValue,
  cfstDefaults,
}: UseSettingsActionsOptions) => {
  const authActions = useSettingsAuthActions({
    authInitialized,
    authForm,
    savingAuth,
    toast,
    ensurePageDataReady,
    markPageDataStale,
    setPageStatusBanner,
  });

  const cfstActions = useSettingsCfstActions({
    cfstForm,
    savingCfst,
    runningCfst,
    cfstStatus,
    cfstResults,
    cfstBestIp,
    cfstResultFile,
    cfstLastUpdated,
    toast,
    ensurePageDataReady,
    markPageDataStale,
    fetchCfstStatus,
    setPageStatusBanner,
    getCfstNumberValue,
    getCfstStringValue,
    cfstDefaults,
  });

  const ikuaiActions = useSettingsIkuaiActions({
    ikuaiDnsForm,
    savingIkuaiDns,
    testingIkuaiDns,
    syncingIkuaiDns,
    exportingIkuaiDns,
    importingIkuaiDns,
    toast,
    ensurePageDataReady,
    markPageDataStale,
    setPageStatusBanner,
  });

  const notifyActions = useSettingsNotifyActions({
    notifyChannels,
    showNotifyModal,
    editingNotifyChannelId,
    editingNotifyChannel,
    testingChannel,
    toast,
    confirm,
    ensurePageDataReady,
    markPageDataStale,
    toNotifyPayload,
    setPageStatusBanner,
  });

  const backupActions = useSettingsBackupActions({
    backupForm,
    backups,
    savingBackup,
    testingConnection,
    runningBackup,
    restoringBackup,
    deletingBackupId,
    showBackupModal,
    loadingBackups,
    toast,
    confirm,
    ensurePageDataReady,
    markPageDataStale,
    setPageStatusBanner,
  });

  return {
    ...authActions,
    ...cfstActions,
    ...ikuaiActions,
    ...notifyActions,
    ...backupActions,
  };
};
