import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { NotifyChannelConfig } from '@/api/notify';

export const useNotifyStore = defineStore('notify', () => {
  const channels = ref<NotifyChannelConfig[]>([]);
  const loading = ref(false);
  const saving = ref(false);
  const testingChannelId = ref<string | null>(null);
  const error = ref<string | null>(null);

  const setChannels = (nextChannels: NotifyChannelConfig[]) => {
    channels.value = nextChannels;
  };

  const setLoading = (nextLoading: boolean) => {
    loading.value = nextLoading;
  };

  const setSaving = (nextSaving: boolean) => {
    saving.value = nextSaving;
  };

  const setTestingChannelId = (channelId: string | null) => {
    testingChannelId.value = channelId;
  };

  const setError = (message: string | null) => {
    error.value = message;
  };

  const reset = () => {
    channels.value = [];
    loading.value = false;
    saving.value = false;
    testingChannelId.value = null;
    error.value = null;
  };

  return {
    channels,
    loading,
    saving,
    testingChannelId,
    error,
    setChannels,
    setLoading,
    setSaving,
    setTestingChannelId,
    setError,
    reset,
  };
});
