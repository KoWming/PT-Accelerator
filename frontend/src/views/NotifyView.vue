<template>
  <SettingsPageShell
    page-title="通知渠道"
    context-title="通知推送管理"
    description=""
    :loaded="hasLoadedNotifyPage"
    :refreshing="pageRefreshing"
    :overview-cards="[]"
    :feedback="statusBanner"
    page-class="notify-page-redesign"
    kicker=""
    :hide-context-panel="true"
    :hide-status-banner="true"
    @refresh="refreshNotifyPage"
  >
    <NotificationSettingsSection
      :notify-channels="notifyChannels"
      :show-notify-modal="showNotifyModal"
      :editing-notify-channel-id="editingNotifyChannelId"
      :editing-notify-channel="editingNotifyChannel"
      :testing-channel="testingChannel"
      @add-channel="openAddNotifyChannelModal"
      @toggle-channel="toggleNotifyChannel"
      @test-channel="testNotifyChannel"
      @edit-channel="editNotifyChannel"
      @delete-channel="deleteNotifyChannel"
      @close-modal="closeNotifyModal"
      @save-channel="saveNotifyChannel"
    />
  </SettingsPageShell>
</template>

<script setup lang="ts">
import '@/assets/styles/settings.css';
import { onMounted, ref } from 'vue';
import { useToast } from '@/composables/useToast';
import NotificationSettingsSection from '@/components/settings/notify/NotificationSettingsSection.vue';
import SettingsPageShell from '@/components/settings/shared/SettingsPageShell.vue';
import { notify } from '@/api';
import { useConfirm } from '@/composables/useConfirm';
import { useSettingsNotifyActions } from '@/composables/useSettingsNotifyActions';
import { getErrorMessage } from '@/utils/error';
import { normalizeNotifyType, pickNotifyConfig } from '@/utils/notify';
import type {
  NotifyChannel,
  NotifyChannelPayload,
  PageFeedback,
  SettingPageKey,
} from '@/types/settings';
import type { NotifyChannelConfig } from '@/api/notify';

const notifyChannels = ref<NotifyChannel[]>([]);
const hasLoadedNotifyPage = ref(false);
const pageRefreshing = ref(false);
const showNotifyModal = ref(false);
const editingNotifyChannelId = ref<string | null>(null);
const editingNotifyChannel = ref<NotifyChannel | null>(null);
const testingChannel = ref<string | null>(null);
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

const fetchNotifyChannels = async () => {
  const response = await notify.listChannels();
  notifyChannels.value = (response.data?.channels || []).map(normalizeNotifyChannel);
};

const ensureNotifyPageReady = async (_section: SettingPageKey) => {
  if (!hasLoadedNotifyPage.value) {
    await fetchNotifyChannels();
    hasLoadedNotifyPage.value = true;
  }
};

const markNotifyPageStale = (_section: SettingPageKey) => {
  hasLoadedNotifyPage.value = false;
};

const {
  closeNotifyModal,
  openAddNotifyChannelModal,
  editNotifyChannel,
  deleteNotifyChannel,
  toggleNotifyChannel,
  testNotifyChannel,
  saveNotifyChannel,
} = useSettingsNotifyActions({
  notifyChannels,
  showNotifyModal,
  editingNotifyChannelId,
  editingNotifyChannel,
  testingChannel,
  toast,
  confirm,
  ensurePageDataReady: ensureNotifyPageReady,
  markPageDataStale: markNotifyPageStale,
  toNotifyPayload,
  setPageStatusBanner: setStatusBanner,
});

const refreshNotifyPage = async () => {
  pageRefreshing.value = true;
  try {
    markNotifyPageStale('notification');
    await ensureNotifyPageReady('notification');
    setStatusBanner('通知页面已刷新', '当前通知渠道列表已按最新后端状态重新加载。');
  } catch (error: any) {
    const message = getErrorMessage(error, '刷新失败');
    setStatusBanner('通知页面刷新失败', message, 'error');
    toast.error(`通知页面刷新失败: ${message}`);
  } finally {
    pageRefreshing.value = false;
  }
};

onMounted(async () => {
  await ensureNotifyPageReady('notification');
});
</script>

