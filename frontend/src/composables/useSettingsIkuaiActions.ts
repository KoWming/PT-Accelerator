import { ikuai } from '@/api';
import { getErrorMessage } from '@/utils/error';
import type { Ref } from 'vue';
import type { IkuaiDnsFormState, PageFeedback, SettingPageKey } from '@/types/settings';

interface UseSettingsIkuaiActionsOptions {
  ikuaiDnsForm: IkuaiDnsFormState;
  savingIkuaiDns: Ref<boolean>;
  testingIkuaiDns: Ref<boolean>;
  syncingIkuaiDns: Ref<boolean>;
  exportingIkuaiDns: Ref<boolean>;
  importingIkuaiDns: Ref<boolean>;
  toast: {
    success: (message: string) => void;
    error: (message: string) => void;
  };
  ensurePageDataReady: (section: SettingPageKey) => Promise<void>;
  markPageDataStale: (section: SettingPageKey) => void;
  setPageStatusBanner: (
    title: string,
    message: string,
    status?: PageFeedback['status']
  ) => void;
}

export const useSettingsIkuaiActions = ({
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
}: UseSettingsIkuaiActionsOptions) => {
  const reloadIkuaiSection = async (
    title: string,
    message: string,
    toastMessage?: string
  ) => {
    markPageDataStale('ikuai-dns');
    await ensurePageDataReady('ikuai-dns');
    setPageStatusBanner(title, message);
    if (toastMessage) {
      toast.success(toastMessage);
    }
  };

  const normalizeIkuaiHost = (value: string) => {
    const rawUrl = value.trim();
    if (!rawUrl) return '';

    const hasProtocol = /^https?:\/\//i.test(rawUrl);
    const normalizedUrl = hasProtocol ? rawUrl : `http://${rawUrl}`;
    const parsed = new URL(normalizedUrl);
    const useHttps = parsed.protocol === 'https:';
    const port = parsed.port ? Number(parsed.port) : (useHttps ? 443 : 80);
    const isDefaultPort = (useHttps && port === 443) || (!useHttps && port === 80);

    return `${parsed.protocol}//${parsed.hostname}${isDefaultPort ? '' : `:${port}`}`;
  };

  const buildIkuaiDnsPayload = () => {
    const host = normalizeIkuaiHost(ikuaiDnsForm.url || '');

    const payload: Record<string, any> = {
      enabled: Boolean(ikuaiDnsForm.enable),
      host,
      username: ikuaiDnsForm.username || 'admin',
    };

    if (ikuaiDnsForm.password && ikuaiDnsForm.password !== '********') {
      payload.password = ikuaiDnsForm.password;
    }

    return payload;
  };

  const getIkuaiTestPayload = () => ({
    ...buildIkuaiDnsPayload(),
    enabled: true,
  });

  const saveIkuaiDnsSettings = async () => {
    savingIkuaiDns.value = true;
    try {
      await ikuai.saveConfig(buildIkuaiDnsPayload());
      await reloadIkuaiSection(
        '远程同步管理已保存',
        '爱快 DNS 同步开关与连接参数已刷新，可继续执行连接测试。',
        '爱快 DNS 设置已保存'
      );
    } catch (e: any) {
      const message = getErrorMessage(e, '保存失败');
      setPageStatusBanner('远程同步管理保存失败', message, 'error');
      toast.error('保存失败: ' + message);
    } finally {
      savingIkuaiDns.value = false;
    }
  };

  const testIkuaiDnsConnection = async () => {
    testingIkuaiDns.value = true;
    try {
      const response = await ikuai.test(getIkuaiTestPayload());
      const data = response.data;
      if (data?.success) {
        setPageStatusBanner('爱快连接测试成功', data.message || '当前连接参数可正常访问爱快 DNS 接口。');
        toast.success(data.message || '爱快 DNS 连接成功');
      } else {
        setPageStatusBanner('爱快连接测试失败', data?.message || '请检查地址、用户名或密码。', 'error');
        toast.error(data?.message || '爱快 DNS 连接失败');
      }
    } catch (e: any) {
      const message = getErrorMessage(e, '爱快 DNS 连接测试失败');
      setPageStatusBanner('爱快连接测试失败', message, 'error');
      toast.error('爱快 DNS 连接测试失败: ' + message);
    } finally {
      testingIkuaiDns.value = false;
    }
  };

  const syncIkuaiDnsNow = async () => {
    syncingIkuaiDns.value = true;
    try {
      const response = await ikuai.syncNow();
      const data = response.data;
      if (data?.success) {
        const countMsg = data.synced_count ? `（${data.synced_count} 条记录）` : '';
        setPageStatusBanner('手动同步完成', data.message || `爱快 DNS 记录已更新${countMsg}`);
        toast.success(data.message || `爱快 DNS 同步成功${countMsg}`);
      } else {
        setPageStatusBanner('手动同步失败', data?.message || '请检查爱快连接或先执行一次 IP 优选', 'error');
        toast.error(data?.message || '爱快 DNS 手动同步失败');
      }
    } catch (e: any) {
      const message = getErrorMessage(e, '爱快 DNS 手动同步失败');
      setPageStatusBanner('手动同步失败', message, 'error');
      toast.error('爱快 DNS 手动同步失败: ' + message);
    } finally {
      syncingIkuaiDns.value = false;
    }
  };

  const exportIkuaiDns = async () => {
    exportingIkuaiDns.value = true;
    try {
      const response = await ikuai.exportDns();
      // 触发浏览器下载
      const blob = new Blob([response.data as BlobPart], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'ikuai_dns.txt';
      a.click();
      URL.revokeObjectURL(url);
      toast.success('DNS 配置导出成功');
    } catch (e: any) {
      const message = getErrorMessage(e, 'DNS 配置导出失败');
      setPageStatusBanner('DNS 配置导出失败', message, 'error');
      toast.error('DNS 配置导出失败: ' + message);
    } finally {
      exportingIkuaiDns.value = false;
    }
  };

  const importIkuaiDns = async (file: File, append: boolean = false) => {
    importingIkuaiDns.value = true;
    try {
      // 读取文件内容并转 Base64
      const arrayBuffer = await file.arrayBuffer();
      const uint8 = new Uint8Array(arrayBuffer);
      let binary = '';
      uint8.forEach((b) => (binary += String.fromCharCode(b)));
      const b64 = btoa(binary);

      const response = await ikuai.importDns(b64, append);
      const data = response.data;
      if (data?.success) {
        setPageStatusBanner('DNS 配置导入成功', data.message || 'DNS 记录已更新');
        toast.success(data.message || 'DNS 配置导入成功');
      } else {
        setPageStatusBanner('DNS 配置导入失败', data?.message || '请检查文件格式或爱快连接', 'error');
        toast.error(data?.message || 'DNS 配置导入失败');
      }
    } catch (e: any) {
      const message = getErrorMessage(e, 'DNS 配置导入失败');
      setPageStatusBanner('DNS 配置导入失败', message, 'error');
      toast.error('DNS 配置导入失败: ' + message);
    } finally {
      importingIkuaiDns.value = false;
    }
  };

  return {
    saveIkuaiDnsSettings,
    testIkuaiDnsConnection,
    syncIkuaiDnsNow,
    exportIkuaiDns,
    importIkuaiDns,
  };
};
