import { notify } from '@/api';
import { getErrorMessage } from '@/utils/error';
import type { Ref } from 'vue';
import type {
  NotifyChannel,
  NotifyChannelPayload,
  PageFeedback,
  SettingPageKey,
} from '@/types/settings';

interface UseSettingsNotifyActionsOptions {
  notifyChannels: Ref<NotifyChannel[]>;
  showNotifyModal: Ref<boolean>;
  editingNotifyChannelId: Ref<string | null>;
  editingNotifyChannel: Ref<NotifyChannel | null>;
  testingChannel: Ref<string | null>;
  toast: {
    success: (message: string) => void;
    error: (message: string) => void;
  };
  confirm: (message: string, title?: string) => Promise<boolean>;
  ensurePageDataReady: (section: SettingPageKey) => Promise<void>;
  markPageDataStale: (section: SettingPageKey) => void;
  toNotifyPayload: (channelData: NotifyChannel) => NotifyChannelPayload;
  setPageStatusBanner: (
    title: string,
    message: string,
    status?: PageFeedback['status']
  ) => void;
}

export const useSettingsNotifyActions = ({
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
}: UseSettingsNotifyActionsOptions) => {
  const reloadNotifySection = async (
    title: string,
    message: string,
    toastMessage?: string
  ) => {
    markPageDataStale('notification');
    await ensurePageDataReady('notification');
    setPageStatusBanner(title, message);
    if (toastMessage) {
      toast.success(toastMessage);
    }
  };

  const closeNotifyModal = () => {
    showNotifyModal.value = false;
    editingNotifyChannelId.value = null;
    editingNotifyChannel.value = null;
  };

  const openAddNotifyChannelModal = () => {
    editingNotifyChannelId.value = null;
    editingNotifyChannel.value = null;
    showNotifyModal.value = true;
  };

  const editNotifyChannel = (channelId: string) => {
    editingNotifyChannelId.value = channelId;
    const channel = notifyChannels.value.find((item) => item.id === channelId);
    if (channel) {
      editingNotifyChannel.value = { ...channel };
      showNotifyModal.value = true;
    }
  };

  const deleteNotifyChannel = async (channelId: string) => {
    if (!await confirm('确定要删除此通知渠道吗？', '删除确认')) return;

    try {
      await notify.deleteChannel(channelId);
      await reloadNotifySection(
        '通知渠道已删除',
        '通知渠道列表已按最新状态重新加载。',
        '通知渠道已删除'
      );
    } catch (e: any) {
      const message = getErrorMessage(e, '删除通知渠道失败');
      setPageStatusBanner('通知渠道删除失败', message, 'error');
      toast.error('删除通知渠道失败: ' + message);
    }
  };

  const toggleNotifyChannel = async (channel: NotifyChannel) => {
    try {
      await notify.updateChannel(channel.id, {
        ...toNotifyPayload(channel),
        enabled: !channel.enabled,
      });
      await reloadNotifySection(
        '通知渠道状态已更新',
        `渠道“${channel.name}”的启停状态已刷新。`
      );
    } catch (e: any) {
      const message = getErrorMessage(e, '更新通知渠道状态失败');
      setPageStatusBanner('通知渠道状态更新失败', message, 'error');
      toast.error('更新通知渠道状态失败: ' + message);
    }
  };

  const testNotifyChannel = async (channelId: string) => {
    testingChannel.value = channelId;
    try {
      await notify.testChannel(channelId);
      setPageStatusBanner('通知渠道测试成功', '测试消息已发送，可到对应渠道确认是否收到。');
      toast.success('通知渠道测试消息已发送');
    } catch (e: any) {
      const message = getErrorMessage(e, '测试通知渠道失败');
      setPageStatusBanner('通知渠道测试失败', message, 'error');
      toast.error('测试通知渠道失败: ' + message);
    } finally {
      testingChannel.value = null;
    }
  };

  const saveNotifyChannel = async (channelData: NotifyChannel) => {
    try {
      const payload = toNotifyPayload(channelData);

      if (editingNotifyChannelId.value) {
        await notify.updateChannel(editingNotifyChannelId.value, payload);
      } else {
        await notify.createChannel(payload);
      }

      await reloadNotifySection(
        '通知渠道已保存',
        '渠道配置已刷新，可直接继续测试发送或调整启停状态。',
        '通知渠道已保存'
      );
      closeNotifyModal();
    } catch (e: any) {
      const message = getErrorMessage(e, '保存通知渠道失败');
      setPageStatusBanner('通知渠道保存失败', message, 'error');
      toast.error('保存通知渠道失败: ' + message);
    }
  };

  return {
    closeNotifyModal,
    openAddNotifyChannelModal,
    editNotifyChannel,
    deleteNotifyChannel,
    toggleNotifyChannel,
    testNotifyChannel,
    saveNotifyChannel,
  };
};
