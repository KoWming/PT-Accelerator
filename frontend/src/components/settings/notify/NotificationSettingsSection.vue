<template>
  <div class="settings-section-shell">
    <article class="workspace-card settings-notify-card">
      <header class="workspace-card-header settings-section-header">
        <div class="settings-card-heading">
          <div class="settings-card-title-row">
            <h3>
              通知渠道
              <span class="settings-title-count">({{ notifyChannels.length }}个)</span>
            </h3>
            <button class="settings-toolbar-btn settings-toolbar-btn-primary" @click="$emit('add-channel')">
              <i class="bx bx-plus"></i>
              <span>添加渠道</span>
            </button>
          </div>
          <p>统一管理 13 种通知推送渠道的启用状态、参数配置、测试发送与编辑维护操作，类型定义与字段说明现已按共享元数据统一。</p>
        </div>
      </header>

      <div class="settings-section-body">
        <div v-if="notifyChannels.length === 0" class="workspace-empty settings-empty-state">
          <i class="bx bx-bell-off fs-1 d-block mb-3 opacity-50"></i>
          暂无通知渠道
        </div>

        <div v-else class="settings-channel-list">
          <div v-for="channel in notifyChannels" :key="channel.id" class="settings-channel-item transition-hover">
            <div class="d-flex flex-column flex-md-row gap-3">
              <div class="d-flex align-items-center flex-grow-1 min-width-0">
                <div class="settings-channel-icon">
                  <i class="bx" :class="getChannelIcon(String(channel.type))"></i>
                </div>
                <div class="flex-grow-1 min-width-0">
                  <div class="d-flex justify-content-between align-items-center mb-1 gap-2">
                    <h6 class="mb-0 fw-semibold text-break me-2">{{ channel.name }}</h6>
                    <div class="flex-shrink-0 ps-2 d-md-none">
                      <label class="switch">
                        <input type="checkbox" :checked="channel.enabled" @change="$emit('toggle-channel', channel)">
                        <div class="slider">
                          <div class="circle">
                            <svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path></g></svg>
                            <svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path></g></svg>
                          </div>
                        </div>
                      </label>
                    </div>
                  </div>

                  <div class="d-flex align-items-center flex-wrap gap-2 small text-muted">
                    <div class="d-flex gap-2 align-items-center">
                      <span class="settings-chip" :class="getChannelChipClass(String(channel.type))">{{ getChannelTypeLabel(String(channel.type)) }}</span>
                      <span v-if="channel.HITOKOTO" class="settings-chip settings-chip-primary">一言</span>
                    </div>
                    <span class="text-truncate d-inline-block" style="max-width: 100%;">{{ getChannelSummary(channel) }}</span>
                  </div>
                </div>
              </div>

              <div class="settings-channel-actions d-flex align-items-center justify-content-end gap-2 ps-md-3 w-100 w-md-auto mt-2 mt-md-0">
                <div class="d-none d-md-block me-2">
                  <label class="switch">
                    <input type="checkbox" :checked="channel.enabled" @change="$emit('toggle-channel', channel)">
                    <div class="slider">
                      <div class="circle">
                        <svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path></g></svg>
                        <svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path></g></svg>
                      </div>
                    </div>
                  </label>
                </div>
                <button class="settings-action-btn settings-action-success flex-grow-1 flex-md-grow-0 justify-content-center" @click="$emit('test-channel', channel.id)" :disabled="testingChannel === channel.id">
                  <span v-if="testingChannel === channel.id" class="spinner-border spinner-border-sm me-1"></span>
                  <i v-else class="bx bx-send me-1"></i> 测试
                </button>
                <button class="settings-action-btn settings-action-primary flex-grow-1 flex-md-grow-0 justify-content-center" @click="$emit('edit-channel', channel.id)">
                  <i class="bx bx-pencil me-1"></i> 编辑
                </button>
                <button class="settings-action-btn settings-action-danger flex-grow-1 flex-md-grow-0 justify-content-center" @click="$emit('delete-channel', channel.id)">
                  <i class="bx bx-trash me-1"></i> 删除
                </button>
              </div>
            </div>
          </div>
        </div>

        <NotificationForm
          v-if="showNotifyModal"
          :initialData="editingNotifyChannel"
          :isEdit="!!editingNotifyChannelId"
          @close="$emit('close-modal')"
          @save="$emit('save-channel', $event)"
        />

        <div class="settings-guide-panel">
          <div class="settings-guide-header">
            <h6><i class="bx bx-info-circle"></i>通知渠道说明</h6>
          </div>
          <div class="row g-3">
            <div v-for="group in NOTIFY_GUIDE_GROUPS" :key="group.title" class="col-md-6">
              <div class="settings-guide-item h-100">
                <div class="d-flex mb-2"><span class="settings-chip" :class="group.chipClass">{{ group.title }}</span></div>
                <p class="small text-muted mb-0">{{ group.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import NotificationForm from '@/components/forms/NotificationForm.vue';
import {
  getNotifyTypeChipClass,
  getNotifyTypeIcon,
  getNotifyTypeLabel,
  normalizeNotifyType,
  NOTIFY_GUIDE_GROUPS,
} from '@/utils/notify';
import type { NotifyChannel } from '@/types/settings';

defineProps<{
  notifyChannels: NotifyChannel[];
  showNotifyModal: boolean;
  editingNotifyChannelId: string | null;
  editingNotifyChannel: NotifyChannel | null;
  testingChannel: string | null;
}>();

defineEmits<{
  'add-channel': [];
  'toggle-channel': [channel: NotifyChannel];
  'test-channel': [channelId: string];
  'edit-channel': [channelId: string];
  'delete-channel': [channelId: string];
  'close-modal': [];
  'save-channel': [channelData: NotifyChannel];
}>();

const getChannelIcon = (type: string) => getNotifyTypeIcon(type).replace(/^bx\s+/, '');
const getChannelChipClass = (type: string) => getNotifyTypeChipClass(type);
const getChannelTypeLabel = (type: string) => getNotifyTypeLabel(type);

const getChannelSummary = (channel: NotifyChannel) => {
  const type = normalizeNotifyType(String(channel.type || ''));

  switch (type) {
    case 'bark':
      return channel.BARK_PUSH || channel.BARK_URL || '未配置 Bark 地址';
    case 'pushplus':
      return channel.PUSH_PLUS_TOKEN || '未配置 PushPlus Token';
    case 'serverchan':
      return channel.SCTKEY || channel.SENDKEY || '未配置 Server 酱密钥';
    case 'telegram':
      return [channel.TELEGRAM_CHAT_ID, channel.TELEGRAM_BOT_TOKEN].filter(Boolean).join(' / ') || '未配置 Telegram 参数';
    case 'dingtalk':
      return channel.DINGTALK_WEBHOOK || '未配置钉钉 Webhook';
    case 'wecom':
      return channel.QYWX_AM || channel.QYWX_KEY || '未配置企业微信参数';
    case 'feishu':
      return channel.FEISHU_WEBHOOK || '未配置飞书 Webhook';
    case 'gotify':
      return channel.GOTIFY_URL || channel.GOTIFY_TOKEN || '未配置 Gotify 参数';
    case 'ntfy':
      return channel.NTFY_URL || channel.NTFY_TOPIC || '未配置 Ntfy 参数';
    case 'pushdeer':
      return channel.PUSHDEER_KEY || '未配置 PushDeer Key';
    case 'email':
      return channel.EMAIL_HOST || channel.EMAIL_TO || '未配置邮件参数';
    case 'discord':
      return channel.DISCORD_WEBHOOK || '未配置 Discord Webhook';
    case 'webhook':
      return channel.WEBHOOK_URL || '未配置 Webhook 地址';
    default:
      return channel.remark || channel.description || '暂无摘要';
  }
};
</script>
