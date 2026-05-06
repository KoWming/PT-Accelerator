<template>
  <section class="settings-cfst-runtime-panel">
    <div class="settings-cfst-runtime-header">
      <div>
        <h4>运行与结果</h4>
        <p>可直接在当前页面触发 Cloudflare IP 优选，并查看实时状态、最佳 IP 与结果明细。</p>
      </div>
    </div>

    <div class="settings-cfst-status-grid">
      <div class="settings-cfst-status-card">
        <span class="settings-field-label">当前状态</span>
        <strong>{{ cfstStatus.message || (cfstStatus.running ? '运行中' : '空闲') }}</strong>
        <p>{{ cfstStatus.task_id ? `任务 ID：${cfstStatus.task_id}` : '等待任务启动' }}</p>
      </div>
      <div class="settings-cfst-status-card">
        <span class="settings-field-label">最佳 IP</span>
        <strong>{{ cfstBestIp || '--' }}</strong>
        <p>{{ cfstResultFile || '尚未生成结果文件' }}</p>
      </div>
      <div class="settings-cfst-status-card">
        <span class="settings-field-label">结果数量</span>
        <strong>{{ displayedCfstResults.length || (cfstHasError ? cfstResults.length : 0) }}</strong>
        <p>任务 ID：{{ cfstStatus.task_id || '--' }}</p>
      </div>
      <div class="settings-cfst-status-card">
        <span class="settings-field-label">最近更新</span>
        <strong>{{ formatCfstDateTime(cfstLastUpdated || cfstStatus.started_at) }}</strong>
        <p>开始时间：{{ formatCfstDateTime(cfstStatus.started_at) }}</p>
      </div>
    </div>

    <div v-if="cfstHasError" class="settings-inline-note settings-inline-note-warning mt-3" role="alert">
      <i class="bx bx-error-circle"></i>
      <div>
        <span class="settings-inline-note-title">本次优选返回了错误结果。</span>
        <div class="settings-inline-note-text">
          {{ cfstResults.find((item) => item?.error)?.error || '请检查测速参数、二进制输出或网络连通性。' }}
        </div>
      </div>
    </div>

    <div v-if="displayedCfstResults.length > 0 && !cfstHasError" class="settings-cfst-results-table-wrap mt-3">
      <table class="table settings-cfst-results-table align-middle mb-0">
        <thead>
          <tr>
            <th>IP</th>
            <th>已发送</th>
            <th>已接收</th>
            <th>丢包率</th>
            <th>平均延迟</th>
            <th>下载速度</th>
            <th>地区码</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in displayedCfstResults" :key="`${item.ip || 'error'}-${index}`">
            <td>
              <div class="settings-cfst-ip-cell">
                <strong>{{ item.ip || '--' }}</strong>
                <span v-if="index === 0 && item.ip" class="settings-chip settings-chip-primary">Best</span>
              </div>
            </td>
            <td>{{ item.sent ?? '--' }}</td>
            <td>{{ item.received ?? '--' }}</td>
            <td>{{ formatMetric(item.loss_rate, 2, '%') }}</td>
            <td>{{ formatMetric(item.avg_latency, 2, ' ms') }}</td>
            <td>{{ formatMetric(item.download_speed, 2, ' MB/s') }}</td>
            <td>{{ item.location || '--' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="!runningCfst" class="settings-empty-state settings-cfst-empty mt-3">
      <i class="bx bx-radar fs-1 d-block mb-3 opacity-50"></i>
      暂无测速结果，先保存参数再跑一次 Cloudflare IP 优选。
    </div>
  </section>
</template>

<script setup lang="ts">
import type { CfstResultItem, CfstStatusState } from '@/types/settings';

defineProps<{
  cfstStatus: CfstStatusState;
  cfstBestIp: string;
  cfstResultFile: string;
  cfstLastUpdated: string;
  cfstHasError: boolean;
  cfstResults: CfstResultItem[];
  displayedCfstResults: CfstResultItem[];
  visibleCfstResults: CfstResultItem[];
  runningCfst: boolean;
  formatCfstDateTime: (value: string | null) => string;
  formatMetric: (value: number | string | null | undefined, digits?: number, suffix?: string) => string;
}>();
</script>
