import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { cfst } from '@/api';
import type { CfstConfig, CfstResult, CfstResultsOut, CfstStatus } from '@/api/cfst';
import { normalizeError } from '@/utils/error';

export const useCfstStore = defineStore('cfst', () => {
  const config = ref<CfstConfig | null>(null);
  const status = ref<CfstStatus | null>(null);
  const results = ref<CfstResult[]>([]);
  const bestIp = ref<string | null>(null);
  const resultFile = ref<string | null>(null);
  const loading = ref(false);
  const loadingResults = ref(false);
  const saving = ref(false);
  const running = ref(false);
  const error = ref<string | null>(null);
  const lastUpdated = ref<string | null>(null);

  const hasErrorResult = computed(() => results.value.some((item) => Boolean(item.error)));
  const visibleResults = computed(() => {
    if (hasErrorResult.value) return results.value.filter((item) => item.error || item.ip);
    return results.value.filter((item) => item.error || Number(item.download_speed) > 0 || item.ip);
  });

  const setStatus = (nextStatus: CfstStatus | null) => {
    status.value = nextStatus;
    running.value = Boolean(nextStatus?.running);
    lastUpdated.value = new Date().toISOString();
  };

  const applyResults = (data?: CfstResultsOut | null) => {
    results.value = Array.isArray(data?.results) ? data.results : [];
    bestIp.value = data?.best_ip || null;
    resultFile.value = data?.result_file || null;
    lastUpdated.value = new Date().toISOString();
  };

  const setError = (message: string | null) => {
    error.value = message;
  };

  const fetchConfig = async () => {
    loading.value = true;
    error.value = null;

    try {
      const response = await cfst.getConfig();
      config.value = response.data;
      return response.data;
    } catch (err) {
      const normalized = normalizeError(err, '获取 CFST 配置失败');
      error.value = normalized.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const saveConfig = async (payload: Partial<CfstConfig>) => {
    saving.value = true;
    error.value = null;

    try {
      await cfst.updateConfig(payload);
      await fetchConfig();
    } catch (err) {
      const normalized = normalizeError(err, '保存 CFST 配置失败');
      error.value = normalized.message;
      throw err;
    } finally {
      saving.value = false;
    }
  };

  const fetchStatus = async () => {
    error.value = null;

    try {
      const response = await cfst.getStatus();
      setStatus(response.data);
      return response.data;
    } catch (err) {
      const normalized = normalizeError(err, '获取 CFST 状态失败');
      error.value = normalized.message;
      throw err;
    }
  };

  const fetchResults = async () => {
    loadingResults.value = true;
    error.value = null;

    try {
      const response = await cfst.getResults();
      applyResults(response.data);
      return response.data;
    } catch (err) {
      const normalized = normalizeError(err, '获取 CFST 结果失败');
      error.value = normalized.message;
      throw err;
    } finally {
      loadingResults.value = false;
    }
  };

  const runNow = async () => {
    running.value = true;
    error.value = null;

    try {
      const response = await cfst.run();
      await fetchStatus();
      return response.data;
    } catch (err) {
      const normalized = normalizeError(err, '启动 CFST 优选失败');
      error.value = normalized.message;
      throw err;
    } finally {
      running.value = Boolean(status.value?.running);
    }
  };

  const refreshAll = async () => {
    loading.value = true;
    error.value = null;

    try {
      await Promise.all([fetchConfig(), fetchStatus(), fetchResults()]);
    } finally {
      loading.value = false;
    }
  };

  const reset = () => {
    config.value = null;
    status.value = null;
    results.value = [];
    bestIp.value = null;
    resultFile.value = null;
    loading.value = false;
    loadingResults.value = false;
    saving.value = false;
    running.value = false;
    error.value = null;
    lastUpdated.value = null;
  };

  return {
    config,
    status,
    results,
    bestIp,
    resultFile,
    loading,
    loadingResults,
    saving,
    running,
    error,
    lastUpdated,
    hasErrorResult,
    visibleResults,
    setStatus,
    applyResults,
    setError,
    fetchConfig,
    saveConfig,
    fetchStatus,
    fetchResults,
    runNow,
    refreshAll,
    reset,
  };
});
