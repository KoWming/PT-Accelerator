<template>
  <div class="settings-section-shell">
    <!-- 爱快 DNS 内容 -->
    <article class="workspace-card settings-auth-card settings-cfst-card" v-if="activeTab === 'ikuai'">
      <header class="workspace-card-header settings-auth-header">
        <div class="remote-sync-header-content">
          <div class="settings-card-heading">
            <div class="settings-card-title-row">
              <h3>爱快DNS同步</h3>
            </div>
            <p>将优选后的 PT / Tracker 域名解析同步到爱快路由器 DNS，适合通过路由器统一生效的使用场景。</p>
          </div>
          <div class="remote-sync-tabs" role="tablist" aria-label="远程同步类型切换">
            <button
              type="button"
              class="remote-sync-tab is-active"
              @click="$emit('tab-change', 'ikuai')"
            >
              <span class="remote-sync-tab-main">
                <i class="bx bx-router"></i>
                <span>爱快 DNS</span>
              </span>
            </button>
            <button
              type="button"
              class="remote-sync-tab"
              @click="$emit('tab-change', 'mihosts')"
            >
              <span class="remote-sync-tab-main">
                <i class="bx bxl-xiaomi"></i>
                <span>小米路由器</span>
              </span>
            </button>
          </div>
        </div>
      </header>

      <div class="settings-auth-body">
        <form @submit.prevent="$emit('submit')">
          <div class="settings-inline-note" role="alert">
            <i class="bx bx-info-circle"></i>
            <div>
              <span class="settings-inline-note-title">远程同步管理属于可选增强功能。</span>
              <div class="settings-inline-note-text">
                启用后，在 IP 优选成功并完成 Hosts/Tracker 更新后，系统会将 PT / Tracker 相关域名同步到爱快路由器 DNS。
              </div>
            </div>
          </div>

          <section class="settings-form-block">
            <div class="settings-auth-toggle-card settings-backup-toggle-card mb-3">
              <div class="settings-auth-toggle-copy">
                <span class="settings-field-label">同步开关</span>
                <div class="ikuai-toggle-title-row">
                  <strong>启用爱快DNS同步</strong>
                  <label class="switch settings-auth-switch ikuai-toggle-switch-mobile" for="ikuai-dns-enable-mobile">
                    <input type="checkbox" id="ikuai-dns-enable-mobile" :checked="ikuaiDnsForm.enable" @change="updateBooleanField('enable', ($event.target as HTMLInputElement).checked)">
                    <div class="slider"><div class="circle"><svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path></g></svg><svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path></g></svg></div></div>
                  </label>
                </div>
                <p>优选完成后，将 PT / Tracker 相关域名解析同步到爱快路由器 DNS。</p>
              </div>
              <label class="switch settings-auth-switch ikuai-toggle-switch-desktop" for="ikuai-dns-enable">
                <input type="checkbox" id="ikuai-dns-enable" :checked="ikuaiDnsForm.enable" @change="updateBooleanField('enable', ($event.target as HTMLInputElement).checked)">
                <div class="slider"><div class="circle"><svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path></g></svg><svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path></g></svg></div></div>
              </label>
            </div>

            <div class="settings-field-grid ikuai-settings-field-grid">
              <div class="settings-field-card settings-field-card-full">
                <label class="form-label settings-form-label">爱快路由器地址</label>
                <input type="text" class="form-control settings-standalone-input" :value="ikuaiDnsForm.url" placeholder="http://192.168.1.1" @input="updateField('url', ($event.target as HTMLInputElement).value)">
              </div>
              <div class="settings-field-card ikuai-credential-field">
                <label class="form-label settings-form-label">用户名</label>
                <input type="text" class="form-control settings-standalone-input" :value="ikuaiDnsForm.username" placeholder="admin" @input="updateField('username', ($event.target as HTMLInputElement).value)">
              </div>
              <div class="settings-field-card ikuai-credential-field">
                <label class="form-label settings-form-label">密码</label>
                <input type="password" class="form-control settings-standalone-input" :value="ikuaiDnsForm.password" placeholder="请输入爱快密码" @input="updateField('password', ($event.target as HTMLInputElement).value)">
              </div>
            </div>
          </section>

          <div class="settings-inline-actions settings-cfst-bottom-actions mt-2 ikuai-inline-actions">
            <button type="button" class="settings-action-btn settings-action-neutral settings-refresh-like-test-btn justify-content-center" @click="$emit('test')" :disabled="testingIkuaiDns || !ikuaiDnsForm.url || !ikuaiDnsForm.password">
              <span v-if="testingIkuaiDns" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bx bx-plug me-2"></i>测试连接
            </button>

            <button type="button" class="settings-action-btn settings-action-neutral settings-refresh-like-test-btn justify-content-center" @click="$emit('sync-now')" :disabled="syncingIkuaiDns || !ikuaiDnsForm.enable">
              <span v-if="syncingIkuaiDns" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bx bx-refresh me-2"></i>立即同步
            </button>

            <button type="submit" class="settings-save-btn" :disabled="savingIkuaiDns">
              <span>
                <span v-if="savingIkuaiDns" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bx bx-save"></i>
                保存设置
              </span>
            </button>
          </div>
        </form>
      </div>
    </article>

    <!-- 小米路由器内容 -->
    <article class="workspace-card settings-auth-card settings-cfst-card" v-else>
      <header class="workspace-card-header settings-auth-header">
        <div class="remote-sync-header-content">
          <div class="settings-card-heading">
            <div class="settings-card-title-row">
              <h3>小米路由器同步</h3>
            </div>
            <p>将 CFST 优选结果同步到小米路由器的 hosts 文件，通过 gorouter.info 云端 API 写入。</p>
          </div>
          <div class="remote-sync-tabs" role="tablist" aria-label="远程同步类型切换">
            <button
              type="button"
              class="remote-sync-tab"
              @click="$emit('tab-change', 'ikuai')"
            >
              <span class="remote-sync-tab-main">
                <i class="bx bx-router"></i>
                <span>爱快 DNS</span>
              </span>
            </button>
            <button
              type="button"
              class="remote-sync-tab is-active"
              @click="$emit('tab-change', 'mihosts')"
            >
              <span class="remote-sync-tab-main">
                <i class="bx bxl-xiaomi"></i>
                <span>小米路由器</span>
              </span>
            </button>
          </div>
        </div>
      </header>

      <div class="settings-auth-body">
        <slot name="mihosts-form"></slot>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import type { IkuaiDnsFormState } from '@/types/settings';

defineProps<{
  ikuaiDnsForm: IkuaiDnsFormState;
  savingIkuaiDns: boolean;
  testingIkuaiDns: boolean;
  syncingIkuaiDns?: boolean;
  activeTab: 'ikuai' | 'mihosts';
}>();

const emit = defineEmits<{
  (event: 'submit'): void;
  (event: 'test'): void;
  (event: 'sync-now'): void;
  (event: 'tab-change', tab: 'ikuai' | 'mihosts'): void;
  <K extends keyof IkuaiDnsFormState>(event: 'updateField', field: K, value: IkuaiDnsFormState[K]): void;
}>();

const updateField = (field: 'url' | 'username' | 'password', value: string) => {
  emit('updateField', field, value);
};

const updateBooleanField = (field: 'enable', value: boolean) => {
  emit('updateField', field, value);
};
</script>

<style scoped>
/* 标题与选项卡横向布局容器 */
.remote-sync-header-content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.remote-sync-tabs {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem;
  border-radius: 0.95rem;
  border: 1px solid rgba(161, 172, 184, 0.16);
  background: var(--bg-surface-alt);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
  flex: 0 0 auto;
}

.ikuai-toggle-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.ikuai-toggle-switch-mobile {
  display: none;
}

.ikuai-toggle-switch-desktop {
  display: inline-flex;
}

/* 移动端适配 */
@media (max-width: 640px) {
  .settings-cfst-card {
    padding: 1rem;
  }

  .workspace-card-header.settings-auth-header {
    padding: 0 0 1rem;
    border-bottom: none;
  }

  .settings-auth-body {
    padding: 0;
  }

  .remote-sync-header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .remote-sync-tabs {
    width: 100%;
    justify-content: stretch;
  }

  .remote-sync-tab {
    flex: 1 1 50%;
    min-width: 0;
  }

  .ikuai-settings-field-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .ikuai-settings-field-grid .settings-field-card-full {
    grid-column: 1 / -1;
  }

  .ikuai-credential-field {
    min-width: 0;
  }

  .ikuai-inline-actions {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.55rem;
  }

  .ikuai-inline-actions > * {
    min-width: 0;
  }

  .ikuai-inline-actions .settings-action-btn,
  .ikuai-inline-actions .settings-save-btn {
    width: 100%;
    min-width: 0;
    padding-inline: 0.65rem;
    font-size: 0.82rem;
  }

  .settings-auth-toggle-card {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    flex-wrap: nowrap;
    gap: 0.75rem;
  }

  .settings-auth-toggle-copy {
    min-width: 0;
    flex: 1 1 auto;
  }

  .settings-auth-switch {
    flex: 0 0 auto;
  }

  .ikuai-toggle-switch-desktop {
    display: none;
  }

  .ikuai-toggle-switch-mobile {
    display: inline-flex;
  }
}

.remote-sync-tab {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-width: 9rem;
  min-height: 2.5rem;
  padding: 0.55rem 1rem;
  border: 1px solid transparent;
  border-radius: 0.75rem;
  background: transparent;
  color: color-mix(in srgb, var(--text-main) 74%, transparent);
  font-size: 0.88rem;
  font-weight: 700;
  line-height: 1;
  transition: background var(--transition-fast), color var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.remote-sync-tab-main {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-width: 0;
}

.remote-sync-tab-main .bx {
  font-size: 1.05rem;
  flex: 0 0 auto;
  opacity: 0.86;
}

.remote-sync-tab:hover,
.remote-sync-tab:focus-visible {
  color: var(--text-main);
  border-color: rgba(161, 172, 184, 0.14);
  background: rgba(var(--primary-rgb), 0.06);
  box-shadow: 0 0 0 1px rgba(var(--primary-rgb), 0.04);
}

.remote-sync-tab.is-active {
  color: var(--text-heading);
  border-color: rgba(var(--primary-rgb), 0.18);
  background: rgba(var(--primary-rgb), 0.1);
  box-shadow: inset 0 0 0 1px rgba(var(--primary-rgb), 0.08);
}

.remote-sync-tab.is-active .remote-sync-tab-main .bx {
  opacity: 1;
}
</style>
