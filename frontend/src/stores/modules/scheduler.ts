import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { scheduler } from '@/api';
import type { SchedulerJob, SchedulerJobIn } from '@/api/scheduler';
import { normalizeError } from '@/utils/error';

export const useSchedulerStore = defineStore('scheduler', () => {
  const running = ref(false);
  const jobs = ref<SchedulerJob[]>([]);
  const loading = ref(false);
  const saving = ref(false);
  const runningJobId = ref<string | null>(null);
  const error = ref<string | null>(null);

  const enabledJobs = computed(() => jobs.value.filter((job) => job.enabled));
  const disabledJobs = computed(() => jobs.value.filter((job) => !job.enabled));

  const setJobs = (nextJobs: SchedulerJob[]) => {
    jobs.value = nextJobs;
  };

  const setError = (message: string | null) => {
    error.value = message;
  };

  const getJob = (jobId: string) => jobs.value.find((job) => job.job_id === jobId) || null;

  const fetchStatus = async () => {
    loading.value = true;
    error.value = null;

    try {
      const response = await scheduler.status();
      running.value = Boolean(response.data?.running);
      jobs.value = Array.isArray(response.data?.jobs) ? response.data.jobs : [];
    } catch (err) {
      const normalized = normalizeError(err, '获取调度器状态失败');
      error.value = normalized.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const saveJob = async (payload: SchedulerJobIn) => {
    saving.value = true;
    error.value = null;

    try {
      await scheduler.createJob(payload);
      await fetchStatus();
    } catch (err) {
      const normalized = normalizeError(err, '保存调度任务失败');
      error.value = normalized.message;
      throw err;
    } finally {
      saving.value = false;
    }
  };

  const removeJob = async (jobId: string) => {
    loading.value = true;
    error.value = null;

    try {
      await scheduler.deleteJob(jobId);
      await fetchStatus();
    } catch (err) {
      const normalized = normalizeError(err, '删除调度任务失败');
      error.value = normalized.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const setJobEnabled = async (jobId: string, enabled: boolean) => {
    saving.value = true;
    error.value = null;

    try {
      if (enabled) {
        await scheduler.enableJob(jobId);
      } else {
        await scheduler.disableJob(jobId);
      }
      await fetchStatus();
    } catch (err) {
      const normalized = normalizeError(err, enabled ? '启用调度任务失败' : '停用调度任务失败');
      error.value = normalized.message;
      throw err;
    } finally {
      saving.value = false;
    }
  };

  const runJobNow = async (jobId: string) => {
    runningJobId.value = jobId;
    error.value = null;

    try {
      await scheduler.runJob(jobId);
      await fetchStatus();
    } catch (err) {
      const normalized = normalizeError(err, '手动触发调度任务失败');
      error.value = normalized.message;
      throw err;
    } finally {
      runningJobId.value = null;
    }
  };

  return {
    running,
    jobs,
    loading,
    saving,
    runningJobId,
    error,
    enabledJobs,
    disabledJobs,
    setJobs,
    setError,
    getJob,
    fetchStatus,
    saveJob,
    removeJob,
    setJobEnabled,
    runJobNow,
  };
});
