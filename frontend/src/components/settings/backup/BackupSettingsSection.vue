<template>
  <div class="settings-section-shell">
    <article class="workspace-card settings-backup-card">
      <header class="workspace-card-header settings-section-header">
        <div class="settings-card-heading">
          <div class="settings-card-title-row">
            <h3>备份设置</h3>
          </div>
          <p>配置 WebDAV 远程存储、自动备份周期、保留份数与恢复流程，确保配置可快速回滚。</p>
        </div>
      </header>

      <div class="settings-section-body">
        <form @submit.prevent="$emit('submit')">
          <div class="settings-inline-note settings-inline-note-info" role="alert">
            <i class="bx bx-info-circle"></i>
            <div style="min-width: 0;">
              <span class="settings-inline-note-title">配置 WebDAV 以备份系统配置。</span>
              <div class="settings-inline-note-text text-break">
                支持定时自动备份和手动立即备份。备份文件将保存为 backup_YYYYMMDD_HHMMSS.zip。
              </div>
            </div>
          </div>

          <section class="settings-auth-toggle-card settings-backup-toggle-card">
            <div class="settings-auth-toggle-copy">
              <span class="settings-field-label">备份状态</span>
              <div class="backup-toggle-title-row">
                <strong>启用配置备份</strong>
                <label class="switch settings-auth-switch backup-toggle-switch-mobile" for="backup-enable-mobile">
                  <input type="checkbox" id="backup-enable-mobile" :checked="backupForm.enable" @change="updateBooleanField('enable', ($event.target as HTMLInputElement).checked)">
                  <div class="slider">
                    <div class="circle">
                      <svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path></g></svg>
                      <svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path></g></svg>
                    </div>
                  </div>
                </label>
              </div>
              <p>开启后可配置自动备份任务，并支持手动测试、立即备份与恢复历史版本。</p>
            </div>
            <label class="switch settings-auth-switch backup-toggle-switch-desktop" for="backup-enable">
              <input type="checkbox" id="backup-enable" :checked="backupForm.enable" @change="updateBooleanField('enable', ($event.target as HTMLInputElement).checked)">
              <div class="slider">
                <div class="circle">
                  <svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path></g></svg>
                  <svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path></g></svg>
                </div>
              </div>
            </label>
          </section>

          <transition name="fade">
            <div v-if="backupForm.enable" class="settings-auth-form-grid">
              <section class="settings-form-block">
                <div class="settings-block-heading">
                  <h4>远程存储连接</h4>
                  <p>填写 WebDAV 地址与认证信息，用于保存和读取备份文件。</p>
                </div>

                <div class="settings-field-grid">
                  <div class="settings-field-card">
                    <label class="form-label settings-form-label">WebDAV URL</label>
                    <input type="text" class="form-control settings-standalone-input" :value="backupForm.webdav_url" placeholder="https://example.com/dav/" @input="updateStringField('webdav_url', ($event.target as HTMLInputElement).value)">
                  </div>
                  <div class="settings-field-card">
                    <label class="form-label settings-form-label">备份路径</label>
                    <input type="text" class="form-control settings-standalone-input" :value="backupForm.webdav_path" placeholder="/PT-Accelerator" @input="updateStringField('webdav_path', ($event.target as HTMLInputElement).value)">
                    <div class="settings-field-hint">远端 WebDAV 目录，备份文件会上传到该路径下。</div>
                  </div>
                </div>

                <div class="settings-field-grid">
                  <div class="settings-field-card">
                    <label class="form-label settings-form-label">用户名</label>
                    <input type="text" class="form-control settings-standalone-input" :value="backupForm.webdav_username" placeholder="请输入 WebDAV 用户名" @input="updateStringField('webdav_username', ($event.target as HTMLInputElement).value)">
                  </div>
                  <div class="settings-field-card">
                    <label class="form-label settings-form-label">密码</label>
                    <input type="password" class="form-control settings-standalone-input" :value="backupForm.webdav_password" placeholder="请输入 WebDAV 密码" @input="updateStringField('webdav_password', ($event.target as HTMLInputElement).value)">
                  </div>
                </div>
              </section>

              <section class="settings-form-block">
                <div class="settings-block-heading settings-block-heading-inline">
                  <h4>备份策略</h4>
                </div>

                <div class="settings-field-grid">
                  <div class="settings-field-card">
                    <label class="form-label settings-form-label">备份保留份数</label>
                    <input type="number" class="form-control settings-standalone-input" :value="backupForm.backup_count" min="1" placeholder="5" @input="updateNumberField('backup_count', ($event.target as HTMLInputElement).value)">
                    <div class="settings-field-hint">当备份数量超过此限制时，将自动删除最旧的备份。默认保留 5 份。</div>
                  </div>
                  <div class="settings-field-card">
                    <label class="form-label settings-form-label">Cron 表达式 (自动备份时间)</label>
                    <CronInput :model-value="backupForm.cron" @update:model-value="updateStringField('cron', $event)" />
                    <div class="settings-field-hint">默认为每天凌晨 2:00（0 2 * * *）。</div>
                  </div>
                </div>
              </section>
            </div>
          </transition>

          <div class="settings-backup-actions backup-inline-actions">
            <div class="settings-backup-tools backup-inline-tools">
              <button type="button" class="settings-action-btn settings-action-neutral justify-content-center" @click="$emit('test')" :disabled="testingConnection || !backupForm.webdav_url">
                <span v-if="testingConnection" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bx bx-plug me-2"></i>测试连接
              </button>
              <button type="button" class="settings-action-btn settings-action-success justify-content-center" @click="$emit('run-now')" :disabled="runningBackup || !backupForm.enable">
                <span v-if="runningBackup" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bx bx-play-circle me-2"></i>立即备份
              </button>
              <button type="button" class="settings-action-btn settings-action-warning justify-content-center" @click="$emit('open-modal')" :disabled="loadingBackups || !backupForm.webdav_url">
                <span v-if="loadingBackups" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bx bx-reset me-2"></i>备份恢复
              </button>
            </div>
            <div class="backup-save-wrap">
              <button type="submit" class="settings-save-btn" :disabled="savingBackup">
                <span>
                  <span v-if="savingBackup" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bx bx-save"></i>
                  保存设置
                </span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import CronInput from '@/components/forms/CronInput.vue';
import type { BackupFormState } from '@/types/settings';

type BackupStringField = 'webdav_url' | 'webdav_username' | 'webdav_password' | 'webdav_path' | 'cron';

defineProps<{
  backupForm: BackupFormState;
  testingConnection: boolean;
  runningBackup: boolean;
  loadingBackups: boolean;
  savingBackup: boolean;
}>();

const emit = defineEmits<{
  (event: 'submit'): void;
  (event: 'test'): void;
  (event: 'run-now'): void;
  (event: 'open-modal'): void;
  <K extends keyof BackupFormState>(event: 'updateField', field: K, value: BackupFormState[K]): void;
}>();

const updateStringField = (field: BackupStringField, value: string) => {
  emit('updateField', field, value);
};

const updateNumberField = (field: 'backup_count', value: string) => {
  emit('updateField', field, value === '' ? 0 : Number(value));
};

const updateBooleanField = (field: 'enable', value: boolean) => {
  emit('updateField', field, value);
};
</script>

<style scoped>
.backup-toggle-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.backup-toggle-switch-mobile {
  display: none;
}

.backup-toggle-switch-desktop {
  display: inline-flex;
}

@media (max-width: 767.98px) {
  .backup-toggle-switch-desktop {
    display: none;
  }

  .backup-toggle-switch-mobile {
    display: inline-flex;
  }

  .backup-inline-actions {
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.55rem;
    align-items: stretch;
  }

  .backup-inline-tools {
    display: contents;
  }

  .backup-inline-actions > *,
  .backup-inline-tools > * {
    min-width: 0;
    width: 100% !important;
  }

  .backup-save-wrap {
    grid-column: 1 / -1;
    display: flex;
    justify-content: stretch;
    width: 100% !important;
  }

  .backup-inline-actions .settings-action-btn,
  .backup-inline-actions .settings-save-btn {
    min-width: 0;
    width: 100% !important;
    padding-inline: 0.65rem;
    font-size: 0.82rem;
    justify-content: center;
  }

  .backup-inline-actions .settings-save-btn {
    max-width: 100%;
    width: 100% !important;
  }
}
</style>
