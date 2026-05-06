<template>
  <SettingsPageShell
    page-title="安全与认证"
    context-title="管理员认证管理"
    description=""
    :loaded="hasLoadedSystemPage"
    :refreshing="pageRefreshing"
    :overview-cards="[]"
    :feedback="statusBanner"
    page-class="system-page-redesign"
    kicker=""
    :hide-context-panel="true"
    @refresh="refreshSystemPage"
  >
    <SystemSettingsSection
      :auth-initialized="authInitialized"
      :auth-form="authForm"
      :saving-auth="savingAuth"
      @submit="saveAuthSettings"
      @update-field="updateAuthFormField"
    />
  </SettingsPageShell>
</template>

<script setup lang="ts">
import '@/assets/styles/settings.css';
import { onMounted, reactive, ref } from 'vue';
import { useToast } from '@/composables/useToast';
import SystemSettingsSection from '@/components/settings/system/SystemSettingsSection.vue';
import SettingsPageShell from '@/components/settings/shared/SettingsPageShell.vue';
import { settings } from '@/api';
import { useSettingsAuthActions } from '@/composables/useSettingsAuthActions';
import { getErrorMessage } from '@/utils/error';
import type {
  AuthFormState,
  PageFeedback,
  SettingPageKey,
} from '@/types/settings';

interface SettingsConfigAuth {
  username?: string;
}

interface SettingsConfigPayload {
  auth?: SettingsConfigAuth;
}

const authInitialized = ref(false);
const savingAuth = ref(false);
const hasLoadedSystemPage = ref(false);
const pageRefreshing = ref(false);
const toast = useToast();
const statusBanner = ref<PageFeedback>({
  title: '',
  message: '',
  status: 'success',
});

const authForm = reactive<AuthFormState>({
  username: 'admin',
  current_password: '',
  new_password: '',
  confirm_password: '',
});

const setStatusBanner = (title: string, message: string, status: PageFeedback['status'] = 'success') => {
  statusBanner.value = { title, message, status };
};

const fetchAuthSettings = async () => {
  const [settingsResponse, systemInfoResponse] = await Promise.all([
    settings.config(),
    settings.info(),
  ]);

  const data = (settingsResponse.data || {}) as SettingsConfigPayload;
  const systemInfo = systemInfoResponse.data || {};
  const auth = data.auth || {};

  authInitialized.value = Boolean(systemInfo.initialized);
  authForm.username = auth.username || 'admin';
};

const ensureSystemPageReady = async (_section: SettingPageKey) => {
  if (!hasLoadedSystemPage.value) {
    await fetchAuthSettings();
    hasLoadedSystemPage.value = true;
  }
};

const markSystemPageStale = (_section: SettingPageKey) => {
  hasLoadedSystemPage.value = false;
};

const updateAuthFormField = <K extends keyof AuthFormState>(field: K, value: AuthFormState[K]) => {
  authForm[field] = value;
};

const { saveAuthSettings } = useSettingsAuthActions({
  authInitialized,
  authForm,
  savingAuth,
  toast,
  ensurePageDataReady: ensureSystemPageReady,
  markPageDataStale: markSystemPageStale,
  setPageStatusBanner: setStatusBanner,
});



const refreshSystemPage = async () => {
  pageRefreshing.value = true;
  try {
    markSystemPageStale('system');
    await ensureSystemPageReady('system');
    setStatusBanner('安全与认证页面已刷新', '当前管理员认证配置已按最新后端状态重新加载。');
  } catch (error: any) {
    const message = getErrorMessage(error, '刷新失败');
    setStatusBanner('安全与认证页面刷新失败', message, 'error');
    toast.error(`安全与认证页面刷新失败: ${message}`);
  } finally {
    pageRefreshing.value = false;
  }
};

onMounted(async () => {
  await ensureSystemPageReady('system');
});
</script>

<style>
body:not(.dark-mode) input.form-control::placeholder {
  color: #cbd5e1 !important;
  opacity: 1 !important;
}
body:not(.dark-mode) input.form-control::-webkit-input-placeholder {
  color: #cbd5e1 !important;
  opacity: 1 !important;
}

input.form-control::placeholder {
  color: #cbd5e1 !important;
  opacity: 1 !important;
}
input.form-control::-webkit-input-placeholder {
  color: #cbd5e1 !important;
  opacity: 1 !important;
}
</style>
