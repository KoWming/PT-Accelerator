<template>
  <SettingsPageShell
    page-title="备份设置"
    context-title="备份与恢复"
    description=""
    :loaded="hasLoadedBackupPage"
    :refreshing="pageRefreshing"
    :overview-cards="[]"
    :feedback="statusBanner"
    page-class="backup-page-redesign"
    kicker=""
    :hide-context-panel="true"
    @refresh="refreshBackupPage"
  >
    <BackupSettingsSection
      :backup-form="backupForm"
      :testing-connection="testingConnection"
      :running-backup="runningBackup"
      :loading-backups="loadingBackups"
      :saving-backup="savingBackup"
      @submit="saveBackupSettings"
      @test="testBackupConnection"
      @run-now="runBackupNow"
      @open-modal="openBackupModal"
      @update-field="updateBackupFormField"
    />

    <BackupRestoreModal
      :visible="showBackupModal"
      :loading-backups="loadingBackups"
      :backups="backups"
      :restoring-backup="restoringBackup"
      :deleting-backup-id="deletingBackupId"
      :format-backup-time="formatBackupTime"
      :format-size="formatSize"
      @close="showBackupModal = false"
      @restore="(bak) => confirmRestore(bak, 'backup')"
      @delete="deleteBackupItem"
    />
  </SettingsPageShell>
</template>

<script setup lang="ts">
import '@/assets/styles/settings.css';
import { onMounted, reactive, ref } from 'vue';
import { useToast } from '@/composables/useToast';
import BackupSettingsSection from '@/components/settings/backup/BackupSettingsSection.vue';
import BackupRestoreModal from '@/components/settings/backup/BackupRestoreModal.vue';
import SettingsPageShell from '@/components/settings/shared/SettingsPageShell.vue';
import { useConfirm } from '@/composables/useConfirm';
import { useSettingsBackupActions } from '@/composables/useSettingsBackupActions';
import { backup, scheduler } from '@/api';
import type { SchedulerJob } from '@/api/scheduler';
import { formatBackupTime as formatBackupTimeLabel, formatFileSize } from '@/utils/format';
import type { BackupFormState, BackupItem, PageFeedback, SettingPageKey } from '@/types/settings';

interface BackupConfigPayload {
  webdav_enabled?: boolean;
  webdav_url?: string;
  webdav_path?: string;
  webdav_username?: string;
  webdav_password?: string;
  local_keep_count?: number;
}

const backupForm = reactive<BackupFormState>({
  enable: false,
  webdav_url: '',
  webdav_path: '/PT-Accelerator',
  webdav_username: '',
  webdav_password: '',
  cron: '0 2 * * *',
  backup_count: 5,
});

const backups = ref<BackupItem[]>([]);
const hasLoadedBackupPage = ref(false);
const pageRefreshing = ref(false);
const savingBackup = ref(false);
const testingConnection = ref(false);
const runningBackup = ref(false);
const restoringBackup = ref(false);
const deletingBackupId = ref<string | null>(null);
const showBackupModal = ref(false);
const loadingBackups = ref(false);
const toast = useToast();
const { confirm } = useConfirm();
const statusBanner = ref<PageFeedback>({
  title: '',
  message: '',
  status: 'success',
});

const setStatusBanner = (title: string, message: string, status: PageFeedback['status'] = 'success') => {
  statusBanner.value = { title, message, status };
};

const fetchBackupSettings = async () => {
  const [backupResponse, backupJobResponse] = await Promise.all([
    backup.getConfig(),
    scheduler.getJob('backup').catch(() => null),
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
}

const ensureBackupPageReady = async (_section: SettingPageKey) => {
  if (!hasLoadedBackupPage.value) {
    await fetchBackupSettings();
    hasLoadedBackupPage.value = true;
  }
};

const markBackupPageStale = (_section: SettingPageKey) => {
  hasLoadedBackupPage.value = false;
};

const {
  saveBackupSettings,
  testBackupConnection,
  openBackupModal,
  confirmRestore,
  deleteBackupItem,
  runBackupNow,
} = useSettingsBackupActions({
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
  ensurePageDataReady: ensureBackupPageReady,
  markPageDataStale: markBackupPageStale,
  setPageStatusBanner: setStatusBanner,
});

const updateBackupFormField = <K extends keyof BackupFormState>(field: K, value: BackupFormState[K]) => {
  backupForm[field] = value;
};



const refreshBackupPage = async () => {
  pageRefreshing.value = true;
  try {
    markBackupPageStale('backup');
    await ensureBackupPageReady('backup');
    setStatusBanner('备份页面已刷新', '当前备份配置已按最新后端状态重新加载。');
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || '刷新失败';
    setStatusBanner('备份页面刷新失败', message, 'error');
    toast.error(`备份页面刷新失败: ${message}`);
  } finally {
    pageRefreshing.value = false;
  }
};

const formatSize = formatFileSize;
const formatBackupTime = (value: string) => formatBackupTimeLabel(value);

onMounted(async () => {
  await ensureBackupPageReady('backup');
});
</script>

