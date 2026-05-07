<template>
  <article class="workspace-card ikuai-dns-card">
    <!-- 卡片 Header -->
    <header class="workspace-card-header ikuai-dns-card-header">
      <div class="ikuai-dns-card-heading">
        <div class="ikuai-dns-card-title-row">
          <div class="ikuai-dns-title-left">
            <h3>
              DNS 记录列表
              <span class="ikuai-dns-title-count">({{ records.length }} 条)</span>
            </h3>
            <p>当前爱快路由器上的全部 DNS 解析记录，可对每条记录进行启用、停用或删除操作。</p>
          </div>
          <div class="ikuai-dns-header-actions">
            <!-- 导出 DNS -->
            <button
              class="ikuai-dns-header-btn"
              :disabled="exporting"
              @click="$emit('export-dns')"
              title="导出 DNS 配置"
            >
              <span v-if="exporting" class="spinner-border spinner-border-sm"></span>
              <i v-else class="bx bx-download"></i>
              <span>导出</span>
            </button>

            <!-- 导入 DNS -->
            <input
              ref="importFileInput"
              type="file"
              accept=".txt,text/plain"
              class="d-none"
              @change="onImportFileChange"
            />
            <button
              class="ikuai-dns-header-btn"
              :disabled="importing"
              @click="importFileInput?.click()"
              title="导入 DNS 配置"
            >
              <span v-if="importing" class="spinner-border spinner-border-sm"></span>
              <i v-else class="bx bx-upload"></i>
              <span>导入</span>
            </button>

            <!-- 刷新 -->
            <button
              class="ikuai-dns-header-btn"
              :disabled="loading"
              @click="$emit('refresh')"
              title="刷新记录列表"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm"></span>
              <i v-else class="bx bx-refresh"></i>
              <span>刷新</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 表格区域 -->
    <div class="ikuai-dns-content-area">
      <!-- 加载中 -->
      <div v-if="loading && !records.length" class="workspace-empty ikuai-dns-loading">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <span>正在加载 DNS 记录…</span>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!records.length" class="workspace-empty ikuai-dns-empty">
        <i class="bx bx-list-ul"></i>
        <strong>暂无 DNS 记录</strong>
        <span>执行一次 IP 优选并同步后，记录将显示在这里。</span>
      </div>

      <!-- 表格 -->
      <div v-else class="ikuai-dns-table">
        <!-- 表头 -->
        <div class="ikuai-dns-table-header">
          <div class="ikuai-dns-th ikuai-dns-th-status"></div>
          <div class="ikuai-dns-th">域名</div>
          <div class="ikuai-dns-th">解析地址</div>
          <div class="ikuai-dns-th ikuai-dns-th-center">类型</div>
          <div class="ikuai-dns-th">备注</div>
          <div class="ikuai-dns-th ikuai-dns-th-center">操作</div>
        </div>

        <!-- 数据行 -->
        <div class="ikuai-dns-table-body">
          <div
            v-for="record in records"
            :key="String(record.id)"
            class="ikuai-dns-row"
            :class="{ 'ikuai-dns-row--disabled': isDisabled(record) }"
          >
            <!-- 状态开关 -->
            <div class="ikuai-dns-col ikuai-dns-col-status">
              <label class="switch ikuai-dns-switch">
                <input
                  type="checkbox"
                  :checked="!isDisabled(record)"
                  :disabled="isRowBusy(record.id)"
                  @change="toggleDnsSwitch(record, $event)"
                />
                <div class="slider">
                  <div class="circle">
                    <svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg">
                      <g>
                        <path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path>
                      </g>
                    </svg>
                    <svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 24 24" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg">
                      <g>
                        <path data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path>
                      </g>
                    </svg>
                  </div>
                </div>
              </label>
            </div>

            <!-- 域名 -->
            <div class="ikuai-dns-col ikuai-dns-col-domain">{{ record.domain || '—' }}</div>

            <!-- 解析地址 -->
            <div class="ikuai-dns-col ikuai-dns-col-ip">{{ record.dns_addr || record.ip || '—' }}</div>

            <!-- 类型 -->
            <div class="ikuai-dns-col ikuai-dns-col-center">
              <span class="ikuai-dns-badge">{{ record.type || 'IPv4' }}</span>
            </div>

            <!-- 备注 -->
            <div class="ikuai-dns-col ikuai-dns-col-comment">{{ record.comment || '—' }}</div>

            <!-- 操作 -->
            <div class="ikuai-dns-col ikuai-dns-col-actions">
              <button
                class="ikuai-dns-action-btn ikuai-dns-action-danger"
                :disabled="isRowBusy(record.id)"
                @click="onDelete(record)"
                title="删除"
              >
                <span>
                  <span v-if="isDeleting(record.id)" class="spinner-border spinner-border-sm"></span>
                  <i v-else class="bx bx-trash"></i>
                  <span>删除</span>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </article>

  <!-- 删除确认弹窗 -->
  <Teleport to="body">
    <div v-if="confirmTarget" class="dns-confirm-overlay" @click.self="confirmTarget = null">
      <div class="dns-confirm-dialog">
        <div class="dns-confirm-icon">
          <i class="bx bx-error-circle"></i>
        </div>
        <h4>确认删除</h4>
        <p>即将删除 DNS 记录：<strong>{{ confirmTarget.domain }}</strong></p>
        <p class="text-muted" style="font-size: 0.83rem;">该操作不可撤销，删除后需重新同步才能恢复。</p>
        <div class="dns-confirm-btns">
          <button class="ikuai-dns-action-btn ikuai-dns-action-neutral" @click="confirmTarget = null">取消</button>
          <button class="ikuai-dns-action-btn ikuai-dns-action-danger" @click="doDelete">确认删除</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { IkuaiDnsRecord } from '@/api/ikuai';

const props = defineProps<{
  records: IkuaiDnsRecord[];
  loading?: boolean;
  /** 正在 toggle 操作的 id 集合 */
  togglingIds?: (string | number)[];
  /** 正在 delete 操作的 id 集合 */
  deletingIds?: (string | number)[];
  /** 导出中 */
  exporting?: boolean;
  /** 导入中 */
  importing?: boolean;
}>();

const emit = defineEmits<{
  (event: 'refresh'): void;
  (event: 'toggle-record', id: string | number, enable: boolean): void;
  (event: 'delete-record', id: string | number): void;
  (event: 'export-dns'): void;
  (event: 'import-dns', file: File, append: boolean): void;
}>();

// ── 状态判断 ──────────────────────────────────────────────
const isDisabled = (record: IkuaiDnsRecord): boolean => {
  // 爱快 enabled 字段返回 "yes" = 启用，"no" = 停用
  // 兼容数字格式：0 = 停用（部分旧固件）
  const v = record.enabled ?? record.state;
  if (v === undefined || v === null) return false;
  const s = String(v).toLowerCase();
  if (s === 'no') return true;
  if (s === 'yes') return false;
  return s === '0';
};

const isToggling = (id: string | number) =>
  props.togglingIds?.some((t) => String(t) === String(id)) ?? false;

const isDeleting = (id: string | number) =>
  props.deletingIds?.some((d) => String(d) === String(id)) ?? false;

const isRowBusy = (id: string | number) => isToggling(id) || isDeleting(id);

// ── 开关切换 ──────────────────────────────────────────────
const toggleDnsSwitch = (record: IkuaiDnsRecord, event: Event) => {
  const checked = (event.target as HTMLInputElement).checked;
  emit('toggle-record', record.id, checked);
};

// ── 删除确认 ──────────────────────────────────────────────
const confirmTarget = ref<IkuaiDnsRecord | null>(null);

const onDelete = (record: IkuaiDnsRecord) => {
  confirmTarget.value = record;
};

const doDelete = () => {
  if (!confirmTarget.value) return;
  emit('delete-record', confirmTarget.value.id);
  confirmTarget.value = null;
};

// ── 导入文件 ──────────────────────────────────────────────
const importFileInput = ref<HTMLInputElement | null>(null);

const onImportFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (file) {
    emit('import-dns', file, false);
    input.value = '';
  }
};
</script>

<style scoped>
/* ── 卡片基础 ─────────────────────────────────────────── */
.ikuai-dns-card {
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  border-radius: 1.4rem;
  background: var(--bg-surface);
  border: 1px solid rgba(161, 172, 184, 0.14);
  box-shadow: var(--shadow-sm);
}

/* ── Header 区：标题左 + 按钮右 ── */
.ikuai-dns-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.ikuai-dns-card-heading {
  flex: 1 1 240px;
  min-width: 0;
}

.ikuai-dns-card-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.85rem;
  flex-wrap: wrap;
}

.ikuai-dns-title-left {
  min-width: 0;
  flex: 1 1 320px;
}

.workspace-card-header h3 {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-heading);
}

.ikuai-dns-title-count {
  font-size: 0.88rem;
  font-weight: 600;
  color: rgba(105, 122, 141, 0.72);
}

.workspace-card-header p {
  margin: 0.4rem 0 0;
  color: var(--text-muted);
  line-height: 1.65;
}

/* ── 头部按钮组 ── */
.ikuai-dns-header-actions {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
  align-self: center;
}

.ikuai-dns-header-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.48rem 0.85rem;
  border: 1px solid rgba(161, 172, 184, 0.16);
  border-radius: 0.78rem;
  background: var(--bg-surface-alt);
  color: color-mix(in srgb, var(--text-heading) 72%, transparent);
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast), border-color var(--transition-fast), background-color var(--transition-fast);
}

.ikuai-dns-header-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
  border-color: rgba(var(--primary-rgb), 0.28);
  color: var(--primary-color);
  background: rgba(var(--primary-rgb), 0.08);
}

.ikuai-dns-header-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── 内容区 ── */
.ikuai-dns-content-area {
  min-width: 0;
}

/* ── 加载 / 空状态 ── */
.workspace-empty {
  min-height: 8rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  color: var(--text-muted);
  text-align: center;
  border: 1px dashed rgba(161, 172, 184, 0.2);
  border-radius: 1rem;
  padding: 2rem 1.5rem;
}

.workspace-empty i {
  font-size: 2rem;
  opacity: 0.45;
}

.workspace-empty strong {
  color: var(--text-heading);
  font-size: 0.95rem;
  font-weight: 600;
}

.workspace-empty span {
  font-size: 0.82rem;
  color: var(--text-muted);
}

.ikuai-dns-loading .spinner-border {
  width: 1.8rem;
  height: 1.8rem;
}

/* ── 表格容器 ── */
.ikuai-dns-table {
  border: 1px solid rgba(161, 172, 184, 0.12);
  border-radius: 1rem;
  overflow: hidden;
  background: color-mix(in srgb, var(--bg-surface-alt) 72%, transparent);
}

/* ── 表头 ── */
.ikuai-dns-table-header,
.ikuai-dns-row {
  display: grid;
  /* status | domain | ip | type | comment | actions */
  grid-template-columns: 3rem minmax(0, 1.4fr) minmax(0, 1.2fr) 6rem minmax(0, 1fr) 7.5rem;
  column-gap: 0.6rem;
  align-items: center;
}

.ikuai-dns-table-header {
  padding: 0.62rem 0.9rem;
  border-bottom: 1px solid rgba(161, 172, 184, 0.12);
  background: color-mix(in srgb, var(--bg-surface) 86%, transparent);
}

.ikuai-dns-th {
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-muted);
  padding: 0.28rem 0.4rem;
}

.ikuai-dns-th-status {
  text-align: center;
}

.ikuai-dns-th-center {
  text-align: center;
}

/* ── 数据行 ── */
.ikuai-dns-table-body {
  display: flex;
  flex-direction: column;
  border-radius: 0 0 1rem 1rem;
  /* 不设 overflow: hidden，让按钮上浮阴影完整显示 */
}

.ikuai-dns-row {
  padding: 0.56rem 0.9rem;
  padding-bottom: 1.25rem; /* 腾出空间，防止按钮上浮被父级 clip */
  border-bottom: 1px solid rgba(161, 172, 184, 0.12);
  transition: background-color var(--transition-base);
  position: relative;
}

.ikuai-dns-row:last-child {
  border-bottom: none;
}

.ikuai-dns-row:hover {
  background: rgba(161, 172, 184, 0.06);
}

.ikuai-dns-row--disabled {
  opacity: 0.5;
}

/* ── 列基础 ── */
.ikuai-dns-col {
  min-width: 0;
  font-size: 0.85rem;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ── 状态开关 ── */
.ikuai-dns-col-status {
  display: flex;
  align-items: center;
  justify-content: center;
}

.ikuai-dns-switch {
  flex-shrink: 0;
}

/* ── 域名（突出显示） ── */
.ikuai-dns-col-domain {
  font-weight: 600;
  color: var(--text-heading);
  font-family: var(--font-mono, 'SFMono-Regular', Consolas, monospace);
  font-size: 0.86rem;
}

/* ── IP 地址 ── */
.ikuai-dns-col-ip {
  font-family: var(--font-mono, 'SFMono-Regular', Consolas, monospace);
  font-size: 0.84rem;
  color: var(--text-primary);
}

/* ── 类型 Badge ── */
.ikuai-dns-col-center {
  text-align: center;
}

.ikuai-dns-badge {
  display: inline-block;
  padding: 0.1rem 0.55rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  background: rgba(var(--primary-rgb), 0.12);
  color: var(--primary-color);
}

/* ── 备注 ── */
.ikuai-dns-col-comment {
  font-size: 0.82rem;
  color: var(--text-muted);
}

/* ── 操作列 ── */
.ikuai-dns-col-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

/* ── 操作按钮（Tracker 风格） ── */
.ikuai-dns-action-btn {
  flex: 1 1 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  border-radius: 0.78rem;
  min-height: 1.9rem;
  padding: 0.38rem 0.6rem;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast), border-color var(--transition-fast), background-color var(--transition-fast);
}

.ikuai-dns-action-btn span {
  display: inline-flex;
  align-items: center;
  gap: 0.28rem;
  white-space: nowrap;
}

.ikuai-dns-action-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.ikuai-dns-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ikuai-dns-action-success {
  background: rgba(74, 179, 126, 0.1);
  color: var(--success-color, #4ab37e);
  border-color: rgba(74, 179, 126, 0.16);
}

.ikuai-dns-action-success:hover:not(:disabled) {
  background: rgba(74, 179, 126, 0.14);
  border-color: rgba(74, 179, 126, 0.28);
}

.ikuai-dns-action-danger {
  background: rgba(225, 108, 108, 0.1);
  color: var(--danger-color, #c0392b);
  border-color: rgba(225, 108, 108, 0.16);
}

.ikuai-dns-action-danger:hover:not(:disabled) {
  background: rgba(225, 108, 108, 0.14);
  border-color: rgba(225, 108, 108, 0.28);
}

.ikuai-dns-action-neutral {
  background: color-mix(in srgb, var(--bg-surface-alt) 88%, transparent);
  border-color: rgba(161, 172, 184, 0.16);
  color: color-mix(in srgb, var(--text-heading) 74%, var(--text-muted));
}

.ikuai-dns-action-neutral:hover:not(:disabled) {
  background: var(--bg-hover);
}

/* ── 滑动开关（复用 Tracker 样式） ── */
.switch {
  --switch-width: 46px;
  --switch-height: 24px;
  --switch-bg: rgba(161, 172, 184, 0.42);
  --switch-checked-bg: linear-gradient(135deg, color-mix(in srgb, var(--success-color, #4ab37e) 86%, #3dd598) 0%, var(--success-color, #4ab37e) 100%);
  --switch-offset: calc((var(--switch-height) - var(--circle-diameter)) / 2);
  --switch-transition: all .2s cubic-bezier(0.27, 0.2, 0.25, 1.51);
  --circle-diameter: 18px;
  --circle-bg: #fff;
  --circle-shadow: 0 0.125rem 0.5rem rgba(67, 89, 113, 0.24);
  --circle-checked-shadow: 0 0.125rem 0.75rem rgba(74, 179, 126, 0.3);
  --circle-transition: var(--switch-transition);
  --icon-transition: all .2s cubic-bezier(0.27, 0.2, 0.25, 1.51);
  --icon-cross-color: var(--switch-bg);
  --icon-cross-size: 6px;
  --icon-checkmark-color: var(--success-color, #4ab37e);
  --icon-checkmark-size: 10px;
  display: inline-block;
}

.switch input { display: none; }

.switch svg {
  transition: var(--icon-transition);
  position: absolute;
  top: 50%;
  left: 50%;
  height: auto;
}

.switch .checkmark {
  width: var(--icon-checkmark-size);
  color: var(--icon-checkmark-color);
  transform: translate(-50%, -50%) scale(0);
}

.switch .cross {
  width: var(--icon-cross-size);
  color: var(--icon-cross-color);
  transform: translate(-50%, -50%) scale(1);
}

.slider {
  box-sizing: border-box;
  width: var(--switch-width);
  height: var(--switch-height);
  background: var(--switch-bg);
  border-radius: 999px;
  display: flex;
  align-items: center;
  position: relative;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
  transition: var(--switch-transition);
  cursor: pointer;
}

.circle {
  width: var(--circle-diameter);
  height: var(--circle-diameter);
  background: var(--circle-bg);
  border-radius: inherit;
  box-shadow: var(--circle-shadow);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--circle-transition);
  z-index: 1;
  position: absolute;
  top: 50%;
  left: var(--switch-offset);
  transform: translateY(-50%);
}

.switch input:checked + .slider {
  background: var(--switch-checked-bg);
}

.switch input:checked + .slider .checkmark {
  transform: translate(-50%, -50%) scale(1);
}

.switch input:checked + .slider .cross {
  transform: translate(-50%, -50%) scale(0);
}

.switch input:checked + .slider .circle {
  box-shadow: var(--circle-checked-shadow);
}

.switch input:disabled + .slider {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── 删除确认弹窗 ── */
.dns-confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}

.dns-confirm-dialog {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 1.2rem;
  padding: 2rem 2rem 1.5rem;
  max-width: 400px;
  width: 90%;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
}

.dns-confirm-icon {
  font-size: 2.5rem;
  color: #e16c6c;
  margin-bottom: 0.75rem;
  line-height: 1;
}

.dns-confirm-dialog h4 {
  margin: 0 0 0.6rem;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-heading);
}

.dns-confirm-dialog p {
  margin: 0.2rem 0;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.dns-confirm-btns {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  margin-top: 1.25rem;
}

/* ── 响应式：表格在小屏下转为卡片列表 ── */
@media (max-width: 767px) {
  .ikuai-dns-card {
    padding: 1rem;
  }

  .ikuai-dns-header-actions {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    width: 100%;
    gap: 0.5rem;
  }

  .ikuai-dns-header-btn {
    width: 100%;
    min-width: 0;
    justify-content: center;
    padding-inline: 0.6rem;
    font-size: 0.82rem;
  }

  .ikuai-dns-table {
    border-left: 1px solid rgba(161, 172, 184, 0.12);
    border-right: 1px solid rgba(161, 172, 184, 0.12);
  }

  .ikuai-dns-table-header {
    display: none;
  }

  .ikuai-dns-row {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 1rem 0.8rem;
    border-bottom: 1px solid rgba(161, 172, 184, 0.1);
  }

  .ikuai-dns-col-status {
    justify-content: flex-start;
  }

  .ikuai-dns-col {
    width: 100%;
    font-size: 0.85rem;
  }

  .ikuai-dns-col-domain::before { content: '域名: '; font-weight: 600; color: var(--text-muted); }
  .ikuai-dns-col-ip::before { content: '地址: '; font-weight: 600; color: var(--text-muted); }
  .ikuai-dns-col-comment::before { content: '备注: '; font-weight: 600; color: var(--text-muted); }

  .ikuai-dns-col-actions {
    width: 100%;
    justify-content: flex-end;
    flex-direction: row;
    padding-top: 0.35rem;
    border-top: 1px solid rgba(161, 172, 184, 0.08);
  }

  .ikuai-dns-action-btn {
    flex: 0 0 auto;
  }
}
</style>
