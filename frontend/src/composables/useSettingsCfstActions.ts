import { cfst } from '@/api';
import { getErrorMessage } from '@/utils/error';
import type { CfstConfig } from '@/api/cfst';
import type { Ref } from 'vue';

import type {
  CfstFormState,
  CfstResultItem,
  CfstStatusState,
  PageFeedback,
  SettingPageKey,
} from '@/types/settings';

interface UseSettingsCfstActionsOptions {
  cfstForm: CfstFormState;
  savingCfst: Ref<boolean>;
  runningCfst: Ref<boolean>;
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
  ensurePageDataReady: (section: SettingPageKey) => Promise<void>;
  markPageDataStale: (section: SettingPageKey) => void;
  fetchCfstStatus: (silent?: boolean) => Promise<void>;
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

export const useSettingsCfstActions = ({
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
}: UseSettingsCfstActionsOptions) => {
  const reloadCfstSection = async (
    title: string,
    message: string,
    toastMessage?: string
  ) => {
    markPageDataStale('cfst');
    await ensurePageDataReady('cfst');
    setPageStatusBanner(title, message);
    if (toastMessage) {
      toast.success(toastMessage);
    }
  };

  const saveCfstSettings = async () => {
    savingCfst.value = true;
    try {
      const payload: Partial<CfstConfig> & { timeout_seconds: number } = {
        threads: getCfstNumberValue(cfstForm.threads, cfstDefaults.threads),
        ping_times: getCfstNumberValue(cfstForm.ping_times, cfstDefaults.ping_times),
        download_count: getCfstNumberValue(cfstForm.download_count, cfstDefaults.download_count),
        download_time: getCfstNumberValue(cfstForm.download_time, cfstDefaults.download_time),
        timeout_seconds: Math.max(getCfstNumberValue(cfstForm.timeout_seconds, cfstDefaults.timeout_seconds), 30),
        tcp_port: getCfstNumberValue(cfstForm.tcp_port, cfstDefaults.tcp_port),
        url: getCfstStringValue(cfstForm.url, cfstDefaults.url),
        httping: Boolean(cfstForm.httping),
        httping_code: cfstForm.httping_code || '',
        cfcolo: cfstForm.cfcolo || '',
        min_delay: getCfstNumberValue(cfstForm.min_delay, cfstDefaults.min_delay),
        max_delay: getCfstNumberValue(cfstForm.max_delay, cfstDefaults.max_delay),
        max_loss_rate: getCfstNumberValue(cfstForm.max_loss_rate, cfstDefaults.max_loss_rate),
        min_speed: getCfstNumberValue(cfstForm.min_speed, cfstDefaults.min_speed),
        show_count: getCfstNumberValue(cfstForm.show_count, cfstDefaults.show_count),
        test_all: Boolean(cfstForm.test_all),
        disable_download: Boolean(cfstForm.disable_download),
        debug: Boolean(cfstForm.debug),
        additional_args: cfstForm.additional_args || '',
      };

      await cfst.updateConfig(payload);


      await reloadCfstSection(
        'CFST 设置已保存',
        '测速参数、过滤条件和运行结果视图已按最新配置刷新。',
        '测速设置已保存'
      );
    } catch (e: any) {
      const message = getErrorMessage(e, '保存失败');
      setPageStatusBanner('CFST 设置保存失败', message, 'error');
      toast.error('保存失败: ' + message);
    } finally {
      savingCfst.value = false;
    }
  };

  const runCfstNow = async () => {
    if (runningCfst.value) {
      toast.info('Cloudflare IP 优选正在执行，先等它跑完。');
      return;
    }

    runningCfst.value = true;
    try {
      const response = await cfst.run();
      const data = response.data || {};
      cfstResults.value = [];
      cfstBestIp.value = '';
      cfstResultFile.value = '';
      cfstLastUpdated.value = '';
      cfstStatus.value = {
        running: true,
        task_id: data.task_id || null,
        progress: 0,
        result_count: 0,
        message: data.message || 'Cloudflare IP 优选任务已启动',
        started_at: new Date().toISOString(),
      };

      toast.success(data.message || 'Cloudflare IP 优选任务已启动');
      await fetchCfstStatus(true);
    } catch (e: any) {
      runningCfst.value = false;
      toast.error('启动测速失败: ' + getErrorMessage(e, '请求失败，请稍后重试'));
    }
  };

  return {
    saveCfstSettings,
    runCfstNow,
  };
};
