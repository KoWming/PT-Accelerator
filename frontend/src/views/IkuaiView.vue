<template>
  <SettingsPageShell
    page-title="远程同步管理"
    context-title="爱快 DNS 同步"
    description=""
    :loaded="hasLoadedIkuaiPage"
    :refreshing="pageRefreshing"
    :overview-cards="[]"
    :feedback="statusBanner"
    page-class="ikuai-page-redesign"
    kicker=""
    :hide-context-panel="true"
    :hide-status-banner="true"
    @refresh="refreshIkuaiPage"
  >
    <!-- 爱快 DNS 选项卡内容 -->
    <template v-if="activeRemoteTab === 'ikuai'">
      <IkuaiDnsSettingsSection
        :ikuai-dns-form="ikuaiDnsForm"
        :saving-ikuai-dns="savingIkuaiDns"
        :testing-ikuai-dns="testingIkuaiDns"
        :syncing-ikuai-dns="syncingIkuaiDns"
        :active-tab="activeRemoteTab"
        @submit="saveIkuaiDnsSettings"
        @test="testIkuaiDnsConnection"
        @sync-now="syncIkuaiDnsNow"
        @update-field="updateIkuaiDnsFormField"
        @tab-change="(tab: 'ikuai' | 'mihosts') => activeRemoteTab = tab"
      />

      <IkuaiDnsRecordList
        :records="dnsRecords"
        :loading="loadingDnsRecords"
        :toggling-ids="togglingRecordIds"
        :deleting-ids="deletingRecordIds"
        :exporting="exportingIkuaiDns"
        :importing="importingIkuaiDns"
        @refresh="fetchDnsRecords"
        @toggle-record="toggleDnsRecord"
        @delete-record="deleteDnsRecord"
        @export-dns="exportIkuaiDns"
        @import-dns="(file: File, append: boolean) => importIkuaiDns(file, append)"
      />
    </template>

    <!-- 小米路由器选项卡内容 -->
    <template v-else>
      <IkuaiDnsSettingsSection
        :ikuai-dns-form="ikuaiDnsForm"
        :saving-ikuai-dns="savingIkuaiDns"
        :testing-ikuai-dns="testingIkuaiDns"
        :syncing-ikuai-dns="syncingIkuaiDns"
        :active-tab="activeRemoteTab"
        @submit="saveMiHostsSettings"
        @test="testIkuaiDnsConnection"
        @sync-now="syncIkuaiDnsNow"
        @update-field="updateIkuaiDnsFormField"
        @tab-change="(tab: 'ikuai' | 'mihosts') => activeRemoteTab = tab"
      >
        <template #mihosts-form>
          <form @submit.prevent="saveMiHostsSettings">
            <!-- 提示信息 -->
            <div class="settings-inline-note" role="alert">
              <i class="bx bx-info-circle"></i>
              <div>
                <span class="settings-inline-note-title">获取 Token 方式：</span>
                <div class="settings-inline-note-text">
                  可以通过访问米家 → 路由 → 自定义Hosts，点击右上角复制链接，从而获取到对应的访问令牌、设备ID、作用域等数据，如无可用数据，请使用默认值。
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
              <label class="switch settings-auth-switch" for="mihosts-enable">
                <input
                  type="checkbox"
                  id="mihosts-enable"
                  :checked="miHostsForm.enable"
                  @change="miHostsForm.enable = ($event.target as HTMLInputElement).checked"
                >
                <div class="slider">
                  <div class="circle">
                    <svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path></g></svg>
                    <svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path></g></svg>
                  </div>
                </div>
              </label>
            </div>

            <!-- 配置字段：每行三个 -->
            <section class="settings-form-block">
              <div class="settings-field-grid settings-field-grid-3cols">
                <div class="settings-field-card">
                  <label class="form-label settings-form-label">应用ID</label>
                  <input
                    type="text"
                    class="form-control settings-standalone-input"
                    v-model="miHostsForm.app_id"
                    placeholder="请输入appid"
                  >
                </div>
                <div class="settings-field-card">
                  <label class="form-label settings-form-label">设备ID</label>
                  <input
                    type="text"
                    class="form-control settings-standalone-input"
                    v-model="miHostsForm.device_id"
                    placeholder="请输入deviceid"
                  >
                </div>
                <div class="settings-field-card">
                  <label class="form-label settings-form-label">客户端ID</label>
                  <input
                    type="text"
                    class="form-control settings-standalone-input"
                    v-model="miHostsForm.client_id"
                    placeholder="请输入clientid"
                  >
                </div>
                <div class="settings-field-card">
                  <label class="form-label settings-form-label">作用域</label>
                  <input
                    type="text"
                    class="form-control settings-standalone-input"
                    v-model="miHostsForm.scope"
                    placeholder="请输入scope"
                  >
                </div>
                <div class="settings-field-card">
                  <label class="form-label settings-form-label">访问令牌</label>
                  <input
                    type="password"
                    class="form-control settings-standalone-input"
                    v-model="miHostsForm.token"
                    placeholder="请输入token"
                  >
                </div>
                <div class="settings-field-card">
                  <label class="form-label settings-form-label">忽略的IP或域名</label>
                  <input
                    type="text"
                    class="form-control settings-standalone-input"
                    v-model="miHostsForm.ignore"
                    placeholder="如：10.10.10.1|wiki.movie-pilot.org"
                    title="多个域名用分号分隔"
                  >
                </div>
              </div>

              <!-- 忽略域名说明 -->
              <div class="settings-field-card settings-field-card-full mihosts-ignore-note">
                <div class="settings-inline-note settings-inline-note-compact">
                  <i class="bx bx-info-circle"></i>
                  <span class="mihosts-ignore-hint">忽略的IP或域名：不想同步到小米路由器的 tracker 域名，用分号（;）分隔，可留空。</span>
                </div>
              </div>
            </section>

            <!-- 同步状态 -->
            <div v-if="miHostsRemoteCount > 0" class="mihosts-sync-status">
              <i class="bx bx-cloud-download me-1"></i>
              远程 hosts：{{ miHostsRemoteCount }} 条
              <button type="button" class="mihosts-view-btn ms-3" @click="loadMiHostsRemote" :disabled="loadingMiHostsRemote">
                <span v-if="loadingMiHostsRemote" class="spinner-border spinner-border-sm"></span>
                <i v-else class="bx bx-refresh"></i>
                刷新
              </button>
            </div>

            <!-- 操作按钮 -->
            <div class="settings-inline-actions settings-cfst-bottom-actions mt-2">
              <button
                type="button"
                class="settings-action-btn settings-action-neutral settings-refresh-like-test-btn justify-content-center"
                @click="testMiHostsConnection"
                :disabled="testingMiHostsConnection || !miHostsForm.token"
              >
                <span v-if="testingMiHostsConnection" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bx bx-plug me-2"></i>
                测试连接
              </button>

              <button
                type="button"
                class="settings-action-btn settings-action-neutral settings-refresh-like-test-btn justify-content-center"
                @click="syncMiHostsNow"
                :disabled="syncingMiHosts || !miHostsForm.enable"
              >
                <span v-if="syncingMiHosts" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bx bx-refresh me-2"></i>
                立即同步
              </button>

              <button type="submit" class="settings-save-btn" :disabled="savingMiHosts">
                <span>
                  <span v-if="savingMiHosts" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bx bx-save"></i>
                  保存设置
                </span>
              </button>
            </div>
          </form>
        </template>
      </IkuaiDnsSettingsSection>
    </template>
  </SettingsPageShell>
</template>

<script lang="ts">
// 模块级单例：DNS 记录状态，跨路由复用，不随组件销毁而重置
import type { IkuaiDnsRecord } from '@/api/ikuai';

const dnsRecords = ref<IkuaiDnsRecord[]>([]);
const loadingDnsRecords = ref(false);
const togglingRecordIds = ref<(string | number)[]>([]);
const deletingRecordIds = ref<(string | number)[]>([]);

export { dnsRecords, loadingDnsRecords, togglingRecordIds, deletingRecordIds };
</script>

<script setup lang="ts">
import '@/assets/styles/settings.css';
import { onMounted, reactive, ref } from 'vue';
import { useToast } from '@/composables/useToast';
import IkuaiDnsSettingsSection from '@/components/settings/ikuai/IkuaiDnsSettingsSection.vue';
import IkuaiDnsRecordList from '@/components/settings/ikuai/IkuaiDnsRecordList.vue';
import SettingsPageShell from '@/components/settings/shared/SettingsPageShell.vue';
import { ikuai, mihosts, settings } from '@/api';
import { useSettingsIkuaiActions } from '@/composables/useSettingsIkuaiActions';
import { getErrorMessage } from '@/utils/error';
import type { IkuaiStatus } from '@/api/ikuai';
import type {
  IkuaiDnsFormState,
  PageFeedback,
  SettingPageKey,
  MiHostsFormState,
} from '@/types/settings';

// 选项卡状态
const activeRemoteTab = ref<'ikuai' | 'mihosts'>('ikuai');

// 爱快 DNS 表单
const ikuaiDnsForm = reactive<IkuaiDnsFormState>({
  enable: false,
  url: '',
  username: 'admin',
  password: '',
});

// 小米路由器表单（默认值与后端 DEFAULT_CONFIG 一致）
const miHostsForm = reactive<MiHostsFormState>({
  enable: false,
  app_id: '2882303761517675329',
  device_id: '',
  client_id: '2882303761517675329',
  scope: '1+1000+3',
  token: '',
  ignore: '',
});

// 小米路由器状态
const savingMiHosts = ref(false);
const testingMiHostsConnection = ref(false);
const syncingMiHosts = ref(false);
const loadingMiHostsRemote = ref(false);
const miHostsRemoteCount = ref(0);

const hasLoadedIkuaiPage = ref(false);
const pageRefreshing = ref(false);
const savingIkuaiDns = ref(false);
const testingIkuaiDns = ref(false);
const syncingIkuaiDns = ref(false);
const exportingIkuaiDns = ref(false);
const importingIkuaiDns = ref(false);

// DNS 记录列表状态（复用模块级单例，由 <script lang="ts"> 导出）

const toast = useToast();
const statusBanner = ref<PageFeedback>({
  title: '',
  message: '',
  status: 'success',
});

const setStatusBanner = (title: string, message: string, status: PageFeedback['status'] = 'success') => {
  statusBanner.value = { title, message, status };
};

const getIkuaiPasswordValue = (status: IkuaiStatus & { password?: string }) => status.password || '';

const formatIkuaiUrlFromStatus = (status: IkuaiStatus) => status.host || '';

const fetchIkuaiSettings = async () => {
  const ikuaiResponse = await ikuai.getStatus();
  const ikuaiData = (ikuaiResponse.data || {}) as IkuaiStatus & { password?: string };

  ikuaiDnsForm.enable = Boolean(ikuaiData.enabled);
  ikuaiDnsForm.url = formatIkuaiUrlFromStatus(ikuaiData);
  ikuaiDnsForm.username = ikuaiData.username || 'admin';
  ikuaiDnsForm.password = getIkuaiPasswordValue(ikuaiData);
};

const ensureIkuaiPageReady = async (_section: SettingPageKey) => {
  if (!hasLoadedIkuaiPage.value) {
    await fetchIkuaiSettings();
    hasLoadedIkuaiPage.value = true;
  }
};

const markIkuaiPageStale = (_section: SettingPageKey) => {
  hasLoadedIkuaiPage.value = false;
};

const {
  saveIkuaiDnsSettings,
  testIkuaiDnsConnection,
  syncIkuaiDnsNow,
  exportIkuaiDns,
  importIkuaiDns,
} = useSettingsIkuaiActions({
  ikuaiDnsForm,
  savingIkuaiDns,
  testingIkuaiDns,
  syncingIkuaiDns,
  exportingIkuaiDns,
  importingIkuaiDns,
  toast,
  ensurePageDataReady: ensureIkuaiPageReady,
  markPageDataStale: markIkuaiPageStale,
  setPageStatusBanner: setStatusBanner,
});

const updateIkuaiDnsFormField = <K extends keyof IkuaiDnsFormState>(field: K, value: IkuaiDnsFormState[K]) => {
  ikuaiDnsForm[field] = value;
};

const refreshIkuaiPage = async () => {
  pageRefreshing.value = true;
  try {
    markIkuaiPageStale('ikuai-dns');
    await ensureIkuaiPageReady('ikuai-dns');
    await fetchDnsRecords();
    setStatusBanner('远程同步页面已刷新', '当前爱快 DNS 配置已按最新后端状态重新加载。');
  } catch (error: any) {
    const message = getErrorMessage(error, '刷新失败');
    setStatusBanner('远程同步页面刷新失败', message, 'error');
    toast.error(`远程同步页面刷新失败: ${message}`);
  } finally {
    pageRefreshing.value = false;
  }
};

// ── DNS 记录操作 ───────────────────────────────────────────

const fetchDnsRecords = async () => {
  loadingDnsRecords.value = true;
  try {
    const res = await ikuai.getRecords();
    dnsRecords.value = (res.data?.records ?? []) as IkuaiDnsRecord[];
  } catch {
    // 非致命错误，静默处理
    dnsRecords.value = [];
  } finally {
    loadingDnsRecords.value = false;
  }
};

const toggleDnsRecord = async (id: string | number, enable: boolean) => {
  togglingRecordIds.value.push(id);
  try {
    const res = await ikuai.toggleRecord(id, enable);
    if (res.data?.success) {
      toast.success(enable ? `DNS 记录已启用` : `DNS 记录已停用`);
      await fetchDnsRecords();
    } else {
      toast.error(res.data?.message || (enable ? 'DNS 记录启用失败' : 'DNS 记录停用失败'));
    }
  } catch (e: any) {
    toast.error(getErrorMessage(e, enable ? 'DNS 记录启用失败' : 'DNS 记录停用失败'));
  } finally {
    togglingRecordIds.value = togglingRecordIds.value.filter((t) => String(t) !== String(id));
  }
};

const deleteDnsRecord = async (id: string | number) => {
  deletingRecordIds.value.push(id);
  try {
    const res = await ikuai.deleteRecord(id);
    if (res.data?.success) {
      toast.success('DNS 记录已删除');
      dnsRecords.value = dnsRecords.value.filter((r) => String(r.id) !== String(id));
    } else {
      toast.error(res.data?.message || 'DNS 记录删除失败');
    }
  } catch (e: any) {
    toast.error(getErrorMessage(e, 'DNS 记录删除失败'));
  } finally {
    deletingRecordIds.value = deletingRecordIds.value.filter((d) => String(d) !== String(id));
  }
};

// ── 小米路由器操作 ───────────────────────────────────────────

const loadMiHostsStatus = async () => {
  try {
    const res = await mihosts.getStatus();
    const data = res.data;
    miHostsForm.enable = data.enabled;
    miHostsForm.app_id = data.app_id || '2882303761517675329';
    miHostsForm.device_id = data.device_id;
    miHostsForm.client_id = data.client_id || '2882303761517675329';
    miHostsForm.scope = data.scope || '1+1000+3';
    miHostsForm.token = data.token === '********' ? '' : data.token;
    miHostsForm.ignore = data.ignore;
  } catch {
    toast.error('加载小米路由器配置失败');
  }
};

const saveMiHostsSettings = async () => {
  savingMiHosts.value = true;
  try {
    await settings.updateConfig({ mihosts: { ...miHostsForm } });
    toast.success('保存成功');
  } catch (e) {
    toast.error('保存失败：' + (e as Error).message);
  } finally {
    savingMiHosts.value = false;
  }
};

const testMiHostsConnection = async () => {
  testingMiHostsConnection.value = true;
  try {
    const res = await mihosts.test(miHostsForm);
    if (res.data.success) {
      toast.success(res.data.message);
    } else {
      toast.error(res.data.message);
    }
  } catch (e) {
    toast.error('测试连接失败：' + (e as Error).message);
  } finally {
    testingMiHostsConnection.value = false;
  }
};

const syncMiHostsNow = async () => {
  syncingMiHosts.value = true;
  try {
    const res = await mihosts.sync();
    if (res.data.success) {
      toast.success(res.data.message);
      await loadMiHostsRemote();
    } else {
      toast.error(res.data.message);
    }
  } catch (e) {
    toast.error('同步失败：' + (e as Error).message);
  } finally {
    syncingMiHosts.value = false;
  }
};

const loadMiHostsRemote = async () => {
  loadingMiHostsRemote.value = true;
  try {
    const res = await mihosts.getRemoteHosts();
    if (res.data.success) {
      miHostsRemoteCount.value = res.data.count;
    } else {
      miHostsRemoteCount.value = 0;
    }
  } catch {
    miHostsRemoteCount.value = 0;
  } finally {
    loadingMiHostsRemote.value = false;
  }
};

onMounted(async () => {
  await ensureIkuaiPageReady('ikuai-dns');
  // 只在首次访问（缓存为空）时自动加载，用户可点击刷新按钮手动更新
  if (!dnsRecords.value.length) {
    await fetchDnsRecords();
  }
  // 加载小米路由器配置
  await loadMiHostsStatus();
  await loadMiHostsRemote();
});
</script>

<style scoped>
/* 选项卡样式 */
.remote-sync-tabs-card {
  padding: 1.25rem 1.5rem;
}

.remote-sync-tabs-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.remote-sync-tabs-title-row {
  flex: 1 1 280px;
  min-width: 0;
}

.remote-sync-tabs-title-row h3 {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-heading);
}

.remote-sync-tabs-title-row p {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
  font-size: 0.85rem;
  line-height: 1.55;
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

/* 三列布局 */
.settings-field-grid-3cols {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

@media (max-width: 767.98px) {
  .remote-sync-tabs-header {
    flex-direction: column;
  }

  .remote-sync-tabs {
    width: 100%;
    justify-content: stretch;
    flex-wrap: wrap;
  }

  .remote-sync-tab {
    flex: 1 1 100%;
    min-width: 0;
  }

  .settings-field-grid-3cols {
    grid-template-columns: 1fr;
  }
}

/* 小米路由器同步状态 */
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

/* 忽略域名说明 */
.mihosts-ignore-note {
  margin-top: 0.5rem;
}

.mihosts-ignore-hint {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.settings-inline-note-compact {
  padding: 0.5rem 0.75rem;
}
</style>

