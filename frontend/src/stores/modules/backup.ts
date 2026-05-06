import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { BackupInfo } from '@/api/backup';

export const useBackupStore = defineStore('backup', () => {
  const backups = ref<BackupInfo[]>([]);
  const loading = ref(false);
  const creating = ref(false);
  const restoring = ref(false);
  const error = ref<string | null>(null);

  const setBackups = (nextBackups: BackupInfo[]) => {
    backups.value = nextBackups;
  };

  const setLoading = (nextLoading: boolean) => {
    loading.value = nextLoading;
  };

  const setCreating = (nextCreating: boolean) => {
    creating.value = nextCreating;
  };

  const setRestoring = (nextRestoring: boolean) => {
    restoring.value = nextRestoring;
  };

  const setError = (message: string | null) => {
    error.value = message;
  };

  const reset = () => {
    backups.value = [];
    loading.value = false;
    creating.value = false;
    restoring.value = false;
    error.value = null;
  };

  return {
    backups,
    loading,
    creating,
    restoring,
    error,
    setBackups,
    setLoading,
    setCreating,
    setRestoring,
    setError,
    reset,
  };
});
