import { backup, scheduler } from '@/api';
import { getErrorMessage } from '@/utils/error';
import type { Ref } from 'vue';
import type {
  BackupFormState,
  BackupItem,
  PageFeedback,
  SettingPageKey,
} from '@/types/settings';

interface UseSettingsBackupActionsOptions {
  backupForm: BackupFormState;
  backups: Ref<BackupItem[]>;
  savingBackup: Ref<boolean>;
  testingConnection: Ref<boolean>;
  runningBackup: Ref<boolean>;
  restoringBackup: Ref<boolean>;
  deletingBackupId: Ref<string | null>;
  showBackupModal: Ref<boolean>;
  loadingBackups: Ref<boolean>;
  toast: {
    success: (message: string) => void;
    error: (message: string) => void;
  };
  confirm: (message: string, title?: string) => Promise<boolean>;
  ensurePageDataReady: (section: SettingPageKey) => Promise<void>;
  markPageDataStale: (section: SettingPageKey) => void;
  setPageStatusBanner: (
    title: string,
    message: string,
    status?: PageFeedback['status']
  ) => void;
}

export const useSettingsBackupActions = ({
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
}: UseSettingsBackupActionsOptions) => {
  const reloadBackupSection = async (
    title: string,
    message: string,
    toastMessage?: string
  ) => {
    markPageDataStale('backup');
    await ensurePageDataReady('backup');
    setPageStatusBanner(title, message);
    if (toastMessage) {
      toast.success(toastMessage);
    }
  };

  const saveBackupSettings = async () => {
    savingBackup.value = true;
    try {
      const backupPayload: Record<string, unknown> = {
        webdav_enabled: backupForm.enable,
        webdav_url: backupForm.webdav_url,
        webdav_username: backupForm.webdav_username,
        webdav_path: backupForm.webdav_path || '/PT-Accelerator',
        local_keep_count: backupForm.backup_count,
      };

      if (backupForm.webdav_password && backupForm.webdav_password !== '********') {
        backupPayload.webdav_password = backupForm.webdav_password;
      }

      await backup.updateConfig(backupPayload);
      await scheduler.createJob({
        job_id: 'backup',
        name: '配置备份任务',
        trigger: 'cron',
        enabled: backupForm.enable,
        cron_expr: backupForm.cron,
      });

      await reloadBackupSection(
        '备份设置已保存',
        'WebDAV 参数与自动备份任务已按最新配置重新加载。',
        '备份设置已保存'
      );
    } catch (e: any) {
      const message = getErrorMessage(e, '保存失败');
      setPageStatusBanner('备份设置保存失败', message, 'error');
      toast.error('保存失败: ' + message);
    } finally {
      savingBackup.value = false;
    }
  };

  const testBackupConnection = async () => {
    testingConnection.value = true;
    try {
      await backup.test({
        webdav_url: backupForm.webdav_url || '',
        webdav_username: backupForm.webdav_username || '',
        webdav_password: backupForm.webdav_password && backupForm.webdav_password !== '********' ? backupForm.webdav_password : '',
        webdav_path: backupForm.webdav_path || '/PT-Accelerator',
      });
      setPageStatusBanner('WebDAV 连接测试成功', '当前远程存储参数可用，可以继续保存设置或执行立即备份。');
      toast.success('WebDAV 连接测试成功');
    } catch (e: any) {
      const message = getErrorMessage(e, '测试失败');
      setPageStatusBanner('WebDAV 连接测试失败', message, 'error');
      toast.error('测试失败: ' + message);
    } finally {
      testingConnection.value = false;
    }
  };

  const openBackupModal = async () => {
    showBackupModal.value = true;
    loadingBackups.value = true;
    try {
      const response = await backup.list();
      backups.value = response.data?.backups || [];
      setPageStatusBanner('备份列表已刷新', `当前可恢复备份数量：${backups.value.length}。`);
    } catch (e: any) {
      const message = getErrorMessage(e, '获取备份列表失败');
      setPageStatusBanner('获取备份列表失败', message, 'error');
      toast.error('获取备份列表失败: ' + message);
    } finally {
      loadingBackups.value = false;
    }
  };

  const confirmRestore = async (bak: BackupItem, activeSection: SettingPageKey) => {
    const backupName = bak.file || bak.filename || bak.id || '当前备份';
    const backupSource = bak.source === 'remote' ? '远程' : '本地';
    if (!await confirm(`确定要恢复${backupSource}备份 ${backupName} 吗？\n当前配置将被覆盖！`, '恢复确认')) return;

    restoringBackup.value = true;
    try {
      await backup.restore(bak.id);
      toast.success('恢复成功');
      showBackupModal.value = false;
      markPageDataStale(activeSection);
      await ensurePageDataReady(activeSection);
      setPageStatusBanner('备份已恢复', `${backupSource}备份 ${backupName} 已恢复，当前分区数据已重新加载。`);
    } catch (e: any) {
      const message = getErrorMessage(e, '恢复失败');
      setPageStatusBanner('备份恢复失败', message, 'error');
      toast.error('恢复失败: ' + message);
    } finally {
      restoringBackup.value = false;
    }
  };

  const deleteBackupItem = async (bak: BackupItem) => {
    const backupName = bak.file || bak.filename || bak.id || '当前备份';
    const backupSource = bak.source === 'remote' ? '远程' : '本地';
    if (!await confirm(`确定要删除${backupSource}备份 ${backupName} 吗？\n删除后将无法恢复。`, '删除确认')) return;

    deletingBackupId.value = bak.id;
    try {
      await backup.delete(bak.id);
      backups.value = backups.value.filter((item) => item.id !== bak.id);
      setPageStatusBanner('备份已删除', `${backupSource}备份 ${backupName} 已删除。`);
      toast.success('备份已删除');
    } catch (e: any) {
      const message = getErrorMessage(e, '删除备份失败');
      setPageStatusBanner('删除备份失败', message, 'error');
      toast.error('删除备份失败: ' + message);
    } finally {
      deletingBackupId.value = null;
    }
  };

  const runBackupNow = async () => {
    if (!await confirm('确定要立即执行备份吗？', '备份确认')) return;

    runningBackup.value = true;
    try {
      await backup.run();
      setPageStatusBanner('立即备份已启动', '系统已开始执行当前备份任务，可稍后打开备份恢复查看最新结果。');
      toast.success('备份任务已启动');
    } catch (e: any) {
      const message = getErrorMessage(e, '执行失败');
      setPageStatusBanner('立即备份启动失败', message, 'error');
      toast.error('执行失败: ' + message);
    } finally {
      runningBackup.value = false;
    }
  };

  return {
    saveBackupSettings,
    testBackupConnection,
    openBackupModal,
    confirmRestore,
    deleteBackupItem,
    runBackupNow,
  };
};
