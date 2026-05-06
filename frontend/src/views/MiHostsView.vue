<template>
  <SettingsPageShell
    page-title="小米路由器同步"
    context-title="小米路由器 Hosts 同步"
    description=""
    :loaded="hasLoadedPage"
    :refreshing="pageRefreshing"
    :overview-cards="[]"
    :feedback="statusBanner"
    page-class="mihosts-page"
    kicker=""
    :hide-context-panel="true"
    :hide-status-banner="true"
    @refresh="loadStatus"
  >
    <!-- 小米路由器设置卡片 -->
    <article class="workspace-card settings-auth-card settings-cfst-card">
      <header class="workspace-card-header settings-auth-header">
        <div class="settings-card-heading">
          <div class="settings-card-title-row">
            <h3>小米路由器</h3>
          </div>
          <p>将 CFST 优选结果同步到小米路由器的 hosts 文件，通过 gorouter.info 云端 API 写入。</p>
        </div>
      </header>

      <div class="settings-auth-body">
        <form @submit.prevent="saveSettings">
          <!-- 提示信息 -->
          <div class="settings-inline-note" role="alert">
            <i class="bx bx-info-circle"></i>
            <div>
              <span class="settings-inline-note-title">获取 Token 方式：</span>
              <div class="settings-inline-note-text">
                登录小米路由器后台（router.miwifi.com）→ 高级设置 → 自定义 hosts → 扫码授权获取 Token。
              </div>
            </div>
          </div>

          <!-- 同步开关 -->
          <div class="settings-auth-toggle-card settings-backup-toggle-card mb-3">
            <div class="settings-auth-toggle-copy">
              <span class="settings-field-label">同步开关</span>
              <strong>启用小米路由器同步</strong>
              <p>CFST 优选成功后，将 tracker 最优 IP 同步到小米路由器 hosts。</p>
            </div>
            <label class="switch settings-auth-switch" :for="'mihosts-enable'">
              <input
                type="checkbox"
                id="mihosts-enable"
                :checked="form.enable"
                @change="form.enable = ($event.target as HTMLInputElement).checked"
              >
              <div class="slider">
                <div class="circle">
                  <svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path></g></svg>
                  <svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path></g></svg>
                </div>
              </div>
            </label>
          </div>

          <!-- 配置字段 -->
          <section class="settings-form-block">
            <div class="settings-field-grid">
              <div class="settings-field-card settings-field-card-full">
                <label class="form-label settings-form-label">App ID</label>
                <input
                  type="text"
                  class="form-control settings-standalone-input"
                  v-model="form.app_id"
                  placeholder="miwifi_app_xxx"
                >
              </div>
              <div class="settings-field-card settings-field-card-full">
                <label class="form-label settings-form-label">Device ID</label>
                <input
                  type="text"
                  class="form-control settings-standalone-input"
                  v-model="form.device_id"
                  placeholder="设备标识"
                >
              </div>
              <div class="settings-field-card settings-field-card-full">
                <label class="form-label settings-form-label">Client ID</label>
                <input
                  type="text"
                  class="form-control settings-standalone-input"
                  v-model="form.client_id"
                  placeholder="OAuth Client ID"
                >
              </div>
              <div class="settings-field-card settings-field-card-full">
                <label class="form-label settings-form-label">Scope</label>
                <input
                  type="text"
                  class="form-control settings-standalone-input"
                  v-model="form.scope"
                  placeholder="app.external"
                >
              </div>
              <div class="settings-field-card settings-field-card-full">
                <label class="form-label settings-form-label">Token</label>
                <input
                  type="password"
                  class="form-control settings-standalone-input"
                  v-model="form.token"
                  placeholder="gorouter.info 授权 Token"
                >
              </div>
              <div class="settings-field-card settings-field-card-full">
                <label class="form-label settings-form-label">忽略域名（每行一个，可留空）</label>
                <textarea
                  class="form-control settings-standalone-input"
                  v-model="form.ignore"
                  rows="3"
                  placeholder="不想同步到小米路由器的域名，每行一个&#10;例如：&#10;example.com&#10;tracker.local"
                ></textarea>
              </div>
            </div>
          </section>

          <!-- 同步状态 -->
          <div v-if="remoteHostsCount > 0" class="mihosts-sync-status">
            <i class="bx bx-cloud-download me-1"></i>
            远程 hosts：{{ remoteHostsCount }} 条
            <button type="button" class="mihosts-view-btn ms-3" @click="loadRemoteHosts" :disabled="loadingRemote">
              <span v-if="loadingRemote" class="spinner-border spinner-border-sm"></span>
              <i v-else class="bx bx-refresh"></i>
              刷新
            </button>
          </div>

          <!-- 操作按钮 -->
          <div class="settings-inline-actions settings-cfst-bottom-actions mt-2">
            <button
              type="button"
              class="settings-action-btn settings-action-neutral settings-refresh-like-test-btn justify-content-center"
              @click="testConnection"
              :disabled="testingConnection || !form.token"
            >
              <span v-if="testingConnection" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bx bx-plug me-2"></i>
              测试连接
            </button>

            <button
              type="button"
              class="settings-action-btn settings-action-neutral settings-refresh-like-test-btn justify-content-center"
              @click="syncNow"
              :disabled="syncing || !form.enable"
            >
              <span v-if="syncing" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bx bx-refresh me-2"></i>
              立即同步
            </button>

            <button type="submit" class="settings-save-btn" :disabled="saving">
              <span>
                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bx bx-save"></i>
                保存设置
              </span>
            </button>
          </div>
        </form>
      </div>
    </article>
  </SettingsPageShell>
</template>

<script setup lang="ts">
import '@/assets/styles/settings.css';
import { onMounted, reactive, ref } from 'vue';
import { useToast } from '@/composables/useToast';
import SettingsPageShell from '@/components/settings/shared/SettingsPageShell.vue';
import { mihosts, settings } from '@/api';
import type { MiHostsFormState, PageFeedback } from '@/types/settings';

const toast = useToast();

const form = reactive<MiHostsFormState>({
  enable: false,
  app_id: '',
  device_id: '',
  client_id: '',
  scope: '',
  token: '',
  ignore: '',
});

const hasLoadedPage = ref(false);
const pageRefreshing = ref(false);
const saving = ref(false);
const testingConnection = ref(false);
const syncing = ref(false);
const loadingRemote = ref(false);
const remoteHostsCount = ref(0);

const statusBanner = ref<PageFeedback>({
  title: '',
  message: '',
  status: 'success',
});

const loadStatus = async () => {
  pageRefreshing.value = true;
  try {
    const res = await mihosts.getStatus();
    const data = res.data;
    form.enable = data.enabled;
    form.app_id = data.app_id;
    form.device_id = data.device_id;
    form.client_id = data.client_id;
    form.scope = data.scope;
    form.token = data.token === '********' ? '' : data.token;
    form.ignore = data.ignore;
    hasLoadedPage.value = true;
  } catch {
    toast.error('加载小米路由器配置失败');
  } finally {
    pageRefreshing.value = false;
  }
};

const saveSettings = async () => {
  saving.value = true;
  try {
    // 保存到 mihosts 配置
    await settings.updateConfig({ mihosts: { ...form } });
    toast.success('保存成功');
  } catch (e) {
    toast.error('保存失败：' + (e as Error).message);
  } finally {
    saving.value = false;
  }
};

const testConnection = async () => {
  testingConnection.value = true;
  try {
    const res = await mihosts.test(form);
    if (res.data.success) {
      toast.success(res.data.message);
    } else {
      toast.error(res.data.message);
    }
  } catch (e) {
    toast.error('测试连接失败：' + (e as Error).message);
  } finally {
    testingConnection.value = false;
  }
};

const syncNow = async () => {
  syncing.value = true;
  try {
    const res = await mihosts.sync();
    if (res.data.success) {
      toast.success(res.data.message);
      await loadRemoteHosts();
    } else {
      toast.error(res.data.message);
    }
  } catch (e) {
    toast.error('同步失败：' + (e as Error).message);
  } finally {
    syncing.value = false;
  }
};

const loadRemoteHosts = async () => {
  loadingRemote.value = true;
  try {
    const res = await mihosts.getRemoteHosts();
    if (res.data.success) {
      remoteHostsCount.value = res.data.count;
    } else {
      remoteHostsCount.value = 0;
    }
  } catch {
    remoteHostsCount.value = 0;
  } finally {
    loadingRemote.value = false;
  }
};

onMounted(async () => {
  await loadStatus();
  await loadRemoteHosts();
});
</script>

<style scoped>
.mihosts-sync-status {
  display: flex;
  align-items: center;
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: color-mix(in srgb, var(--bg-surface-alt) 60%, transparent);
  border-radius: 0.5rem;
  border: 1px solid rgba(161, 172, 184, 0.12);
}

.mihosts-view-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.78rem;
  padding: 0.2rem 0.6rem;
  background: transparent;
  border: 1px solid rgba(161, 172, 184, 0.2);
  border-radius: 0.4rem;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.mihosts-view-btn:hover {
  background: rgba(139, 92, 246, 0.1);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.mihosts-view-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
