<template>
  <div class="dashboard-redesign">
    <div class="page-header">
      <h2 class="page-title">Tracker 管理</h2>
    </div>

    <section class="trackers-layout">
      <article class="workspace-card tracker-actions-card">
        <header class="workspace-card-header tracker-actions-header">
          <div class="tracker-card-heading">
            <div class="tracker-card-title-row">
              <h3>功能操作</h3>
            </div>
            <p>集中处理当前 Tracker 列表的批量 IP 覆盖、Cloudflare IP 优选触发，以及 Cloudflare 域名名单维护。</p>
          </div>
        </header>

        <div class="tracker-actions-body">
          <div class="tracker-actions-top">
            <section class="tracker-primary-action">
              <div class="tracker-primary-action-head">
                <h4>批量覆盖当前 IP</h4>
              </div>



              <div class="tracker-ip-editor tracker-ip-editor-compact">
                <div class="tracker-ip-input-group">
                  <span class="tracker-ip-prefix">目标 IP</span>
                  <input type="text" class="form-control tracker-ip-input" v-model="batchIpDraft" placeholder="例如: 1.1.1.1" :disabled="isUpdatingAllTrackerIp">
                  <button class="action-btn action-btn-primary action-btn-compact tracker-ip-submit" @click="handleBatchUpdateIp" :disabled="isUpdatingAllTrackerIp || !batchIpDraft || !isValidIpv4">

                    <span>
                      <span v-if="isUpdatingAllTrackerIp" class="spinner-border spinner-border-sm"></span>
                      <i v-else class="bx bx-save"></i>
                      <span>应用到全部 Tracker</span>
                    </span>
                  </button>
                </div>
                <div class="tracker-inline-note">
                  <i class="bx bx-info-circle"></i>
                  <span>{{ batchIpHint }}</span>
                </div>
              </div>
            </section>
          </div>

          <section class="tracker-secondary-actions">

            <button class="tracker-mini-action tracker-mini-primary" @click="isAddTrackerModalOpen = true">
              <i class="bx bx-plus-circle"></i>
              <span>新增 Tracker</span>
            </button>

            <button class="tracker-mini-action tracker-mini-info" @click="isBatchImportModalOpen = true">
              <i class="bx bx-list-check"></i>
              <span>批量导入 Tracker</span>
            </button>

            <button class="tracker-mini-action tracker-mini-danger" @click="handleClearAllTrackers" :disabled="!supportsClearAllTrackers || isClearingTrackers" :title="clearAllTrackersHint">
              <span v-if="isClearingTrackers" class="spinner-border spinner-border-sm"></span>
              <i v-else class="bx bx-trash"></i>
              <span>清空 Tracker 列表</span>
            </button>
          </section>





        </div>

      </article>

      <article class="workspace-card trackers-card">
        <header class="workspace-card-header trackers-card-header">
          <div class="tracker-card-heading">
            <div class="tracker-card-title-row tracker-card-title-row-tabs">
              <div>
                <h3>
                  {{ activeTrackerTab === 'trackers' ? 'Tracker 列表' : 'Cloudflare 域名名单' }}
                  <span class="tracker-title-count">({{ activeTrackerTab === 'trackers' ? store.trackers.length : cloudflareDomains.length }} {{ activeTrackerTab === 'trackers' ? '条' : '个域名' }})</span>
                </h3>
                <p>
                  {{ activeTrackerTab === 'trackers'
                    ? '查看当前 Tracker 的名称、目标域名、当前 IP 与启用状态，并可直接加入 Cloudflare 域名名单或删除。'
                    : '集中维护需要按 Cloudflare 域名参与识别与优选 IP 应用的名单，不会直接改动当前 Tracker 列表。' }}
                </p>
              </div>

              <div class="tracker-view-tabs" role="tablist" aria-label="Tracker 视图切换">
                <button
                  type="button"
                  class="tracker-view-tab"
                  :class="{ 'is-active': activeTrackerTab === 'trackers' }"
                  @click="activeTrackerTab = 'trackers'"
                >
                  <span class="tracker-view-tab-main">
                    <i class="bx bx-list-ul"></i>
                    <span>Tracker 列表</span>
                  </span>
                </button>
                <button
                  type="button"
                  class="tracker-view-tab"
                  :class="{ 'is-active': activeTrackerTab === 'cloudflare' }"
                  @click="activeTrackerTab = 'cloudflare'"
                >
                  <span class="tracker-view-tab-main">
                    <i class="bx bx-shield-quarter"></i>
                    <span>Cloudflare 域名名单</span>
                  </span>
                </button>
              </div>
            </div>
          </div>
        </header>

        <div class="trackers-content-area">
          <template v-if="activeTrackerTab === 'trackers'">
            <div v-if="store.loading" class="workspace-empty trackers-loading">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <span>正在加载 Tracker 配置...</span>
            </div>

            <div v-else-if="store.trackers.length === 0" class="workspace-empty trackers-empty">
              <i class="bx bx-data"></i>
              <strong>暂无 Tracker</strong>
              <span>可通过上方操作区添加单个或批量导入 Tracker。</span>
            </div>

            <div v-else class="tracker-table">
              <div class="tracker-table-header">
                <button type="button" class="tracker-sort-btn" :class="getSortButtonClass('name')" @click="handleSort('name')">
                  <span class="tracker-sort-label">名称</span>
                  <span class="tracker-sort-indicator">
                    <i :class="getSortIcon('name')"></i>
                  </span>
                </button>
                <button type="button" class="tracker-sort-btn" :class="getSortButtonClass('url')" @click="handleSort('url')">
                  <span class="tracker-sort-label">域名</span>
                  <span class="tracker-sort-indicator">
                    <i :class="getSortIcon('url')"></i>
                  </span>
                </button>

                <button type="button" class="tracker-sort-btn" :class="getSortButtonClass('ip')" @click="handleSort('ip')">
                  <span class="tracker-sort-label">当前 IP</span>
                  <span class="tracker-sort-indicator">
                    <i :class="getSortIcon('ip')"></i>
                  </span>
                </button>
                <button type="button" class="tracker-sort-btn tracker-sort-btn-center" :class="getSortButtonClass('enabled')" @click="handleSort('enabled')">
                  <span class="tracker-sort-label">开关</span>
                  <span class="tracker-sort-indicator">
                    <i :class="getSortIcon('enabled')"></i>
                  </span>
                </button>
                <div class="tracker-table-action-label">操作</div>
              </div>

              <div class="tracker-table-body">
                <div class="tracker-row" v-for="tracker in sortedTrackers" :key="tracker.id || tracker.url">
                  <div class="tracker-col-name">
                    <strong>{{ tracker.name }}</strong>
                  </div>
                  <div class="tracker-col-network">
                    <div class="tracker-col-domain mono-text" :title="tracker.url">{{ tracker.url }}</div>
                    <div class="tracker-col-ip mono-text">{{ tracker.ip || '未设置' }}</div>
                  </div>
                  <div class="tracker-col-switch">
                    <label class="switch tracker-switch">
                      <input type="checkbox" :checked="tracker.enabled" @change="toggleTracker(tracker)">
                      <div class="slider">
                        <div class="circle">
                          <svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg">
                            <g>
                              <path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path>
                            </g>
                          </svg>
                          <svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg">
                            <g>
                              <path data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path>
                            </g>
                          </svg>
                        </div>
                      </div>
                    </label>
                  </div>
                  <div class="tracker-col-actions">
                    <button class="tracker-action-btn tracker-action-success" @click="addTrackerDomainToCloudflareList(tracker)">
                      <span>
                        <i class="bx bx-shield-plus"></i>
                        <span>加入 Cloudflare 名单</span>
                      </span>
                    </button>

                    <button class="tracker-action-btn tracker-action-danger" @click="confirmDelete(tracker)">
                      <span>
                        <i class="bx bx-trash"></i>
                        <span>删除</span>
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="tracker-cloudflare-tab-content">
              <div class="tracker-whitelist-input-row tracker-whitelist-input-row-inline">
                <div class="input-group tracker-input-group tracker-input-group-flex">
                  <span class="input-group-text"><i class="bx bx-globe"></i></span>
                  <input type="text" class="form-control" v-model="cloudflareDomainDraft" placeholder="如：example.com" @keyup.enter="handleAddCloudflareDomain">
                </div>
                <button class="tracker-modal-btn tracker-modal-btn-primary tracker-whitelist-add-btn" @click="handleAddCloudflareDomain" :disabled="isAddingCloudflareDomain">
                  <span v-if="isAddingCloudflareDomain" class="spinner-border spinner-border-sm"></span>
                  <template v-else>
                    <i class="bx bx-plus"></i>
                    <span>添加域名</span>
                  </template>
                </button>
                <button class="tracker-modal-btn tracker-modal-btn-muted tracker-cloudflare-refresh-btn" @click="() => refreshCloudflareDomains()" :disabled="isLoadingCloudflareDomains">
                  <span v-if="isLoadingCloudflareDomains" class="spinner-border spinner-border-sm"></span>
                  <template v-else>
                    <i class="bx bx-refresh"></i>
                    <span>刷新名单</span>
                  </template>
                </button>
              </div>



              <div v-if="isLoadingCloudflareDomains" class="tracker-whitelist-state">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <span>正在加载域名名单...</span>
              </div>

              <div v-else-if="cloudflareDomains.length === 0" class="tracker-whitelist-state tracker-whitelist-state-empty">
                <i class="bx bx-data"></i>
                <span>暂无 Cloudflare 域名</span>
              </div>

              <div v-else class="tracker-cloudflare-table-wrap">
                <table class="tracker-cloudflare-table">
                  <thead>
                    <tr>
                      <th scope="col"><span class="tracker-cloudflare-domain-cell">域名</span></th>
                      <th scope="col">当前 IP</th>
                      <th scope="col">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="domain in cloudflareDomains" :key="domain" class="tracker-cloudflare-row">
                      <td :title="domain">
                        <span class="tracker-cloudflare-domain-cell">{{ domain }}</span>
                        <span class="tracker-cloudflare-ip-inline mono-text">{{ getCloudflareTrackerIp(domain) }}</span>
                      </td>
                      <td class="tracker-cloudflare-ip-col mono-text">{{ getCloudflareTrackerIp(domain) }}</td>
                      <td class="tracker-cloudflare-actions">
                        <button class="tracker-action-btn tracker-action-danger tracker-cloudflare-delete-btn" @click="handleDeleteCloudflareDomain(domain)">
                          <span>
                            <i class="bx bx-trash"></i>
                            <span>删除</span>
                          </span>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </template>
        </div>
      </article>

    </section>


    <!-- Add Modal -->
    <div v-if="isAddTrackerModalOpen" class="modal fade show d-block tracker-modal" @click.self="isAddTrackerModalOpen = false">
      <div class="modal-dialog modal-lg modal-dialog-centered tracker-modal-dialog">
        <div class="modal-content tracker-modal-content">
          <div class="modal-header tracker-modal-header">
            <div class="tracker-modal-title-wrap">
              <h5 class="modal-title">新增 Tracker</h5>
              <p>填写基础信息后即可快速加入当前 Tracker 列表。</p>
            </div>
            <button type="button" class="btn-close tracker-modal-close" @click="isAddTrackerModalOpen = false"></button>
          </div>
          <div class="modal-body tracker-modal-body">
            <form @submit.prevent="handleAddTracker" class="tracker-modal-form">
              <section class="tracker-form-panel tracker-form-panel-main">
                <div class="tracker-form-panel-head tracker-form-panel-head-inline">
                  <h6>基础配置</h6>
                  <div class="form-check form-switch tracker-switch-item tracker-switch-item-inline">
                    <input class="form-check-input" type="checkbox" id="tracker-enable" v-model="newTracker.enabled">
                    <label class="form-check-label" for="tracker-enable">启用</label>
                  </div>
                </div>

                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label tracker-form-label">名称 <span class="text-danger">*</span></label>
                    <div class="input-group tracker-input-group">
                      <span class="input-group-text"><i class="bx bx-purchase-tag-alt"></i></span>
                      <input type="text" class="form-control" v-model="newTracker.name" required placeholder="如：PTP Tracker">
                    </div>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label tracker-form-label">域名 <span class="text-danger">*</span></label>
                    <div class="input-group tracker-input-group">
                      <span class="input-group-text"><i class="bx bx-globe"></i></span>
                      <input type="text" class="form-control" v-model="newTracker.url" required placeholder="如：tracker.example.com">
                    </div>
                  </div>
                </div>

                <div class="tracker-form-panel-subtle tracker-form-panel-subtle-embedded">
                  <div class="tracker-switch-stack">
                    <div class="form-check form-switch tracker-switch-item">
                      <input class="form-check-input" type="checkbox" id="tracker-force-cloudflare" v-model="forceCloudflare">
                      <label class="form-check-label" for="tracker-force-cloudflare">同时加入 Cloudflare 域名名单</label>
                    </div>
                  </div>
                </div>
              </section>
            </form>
          </div>
          <div class="modal-footer tracker-modal-footer">
            <div class="tracker-modal-footer-note">
              <i class="bx bx-info-circle"></i>
              <span>保存后可在列表中继续维护当前 IP、启用状态与 Cloudflare 域名名单归属。</span>
            </div>
            <div class="tracker-modal-footer-actions">
              <button type="button" class="tracker-modal-btn tracker-modal-btn-muted" @click="isAddTrackerModalOpen = false">取消</button>
              <button type="submit" class="tracker-modal-btn tracker-modal-btn-primary" @click="handleAddTracker" :disabled="isAddingTracker">
                <span v-if="isAddingTracker" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bx bx-save"></i>
                <span>保存 Tracker</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Batch Add Modal -->
    <div v-if="isBatchImportModalOpen" class="modal fade show d-block tracker-modal" @click.self="isBatchImportModalOpen = false">
      <div class="modal-dialog modal-lg modal-dialog-centered tracker-modal-dialog">
        <div class="modal-content tracker-modal-content">
          <div class="modal-header tracker-modal-header">
            <div class="tracker-modal-title-wrap">
              <h5 class="modal-title">批量导入 Tracker</h5>
              <p>按行粘贴域名后即可一次性导入多个站点。</p>
            </div>
            <button type="button" class="btn-close tracker-modal-close" @click="isBatchImportModalOpen = false"></button>
          </div>
          <div class="modal-body tracker-modal-body">
            <div class="tracker-modal-form">
              <section class="tracker-form-panel tracker-form-panel-info">
                <div class="tracker-info-note">
                  <i class="bx bx-info-circle"></i>
                  <div>
                    <strong>导入说明</strong>
                    <span>批量导入的域名会使用当前优选的 Cloudflare IP；若暂无优选结果，则使用默认 IP：104.16.91.215。</span>
                  </div>
                </div>
              </section>

              <section class="tracker-form-panel tracker-form-panel-main">
                <div class="tracker-form-panel-head">
                  <h6>域名列表</h6>
                  <span>每行填写一个域名，保存时会自动按行拆分导入。</span>
                </div>
                <div class="tracker-textarea-shell">
                  <textarea class="form-control tracker-textarea" v-model="batchDomains" placeholder="tracker.example.com"></textarea>
                </div>
              </section>
            </div>
          </div>
          <div class="modal-footer tracker-modal-footer">
            <div class="tracker-modal-footer-note">
              <i class="bx bx-info-circle"></i>
              <span>导入完成后可继续维护当前 IP、启用状态与 Cloudflare 域名名单归属。</span>
            </div>
            <div class="tracker-modal-footer-actions">
              <button type="button" class="tracker-modal-btn tracker-modal-btn-muted" @click="isBatchImportModalOpen = false">取消</button>
              <button type="button" class="tracker-modal-btn tracker-modal-btn-primary" @click="handleBatchAdd" :disabled="isBatchImportingTrackers">
                <span v-if="isBatchImportingTrackers" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bx bx-list-plus"></i>
                <span>导入 Tracker</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue';
import { useTrackerStore, type Tracker } from '@/stores/modules/trackers';
import { useToast } from '@/composables/useToast';
import { useConfirm } from '@/composables/useConfirm';
import { getErrorMessage } from '@/utils/error';

interface TrackerDraft {
  name: string;
  url: string;
  enabled: boolean;
}

const normalizeDomain = (value: string) => {
  const trimmed = (value || '').trim().toLowerCase();
  if (!trimmed) return '';
  try {
    if (trimmed.includes('://')) {
      return new URL(trimmed).hostname.toLowerCase();
    }
  } catch {
    // ignore parse error and fallback to manual extraction
  }
  return ((trimmed.replace(/^[a-z]+:\/\//, '').split('/')[0] ?? '').split(':')[0] ?? '').replace(/\.$/, '');
};

const store = useTrackerStore();
const toast = useToast();
const { confirm } = useConfirm();
const isAddTrackerModalOpen = ref(false);
const isBatchImportModalOpen = ref(false);
const isAddingTracker = ref(false);
const isBatchImportingTrackers = ref(false);
const isUpdatingAllTrackerIp = ref(false);

const isClearingTrackers = ref(false);
const cloudflareDomains = ref<string[]>([]);
const cloudflareDomainDraft = ref('');
const activeTrackerTab = ref<'trackers' | 'cloudflare'>('trackers');
const isLoadingCloudflareDomains = ref(false);

const isAddingCloudflareDomain = ref(false);
const forceCloudflare = ref(false);
const supportsBatchIpUpdate = true;
const supportsClearAllTrackers = true;
const batchIpHint = '请输入合法 IPv4 地址后再执行批量覆盖。此操作会把当前列表中全部 Tracker 的当前 IP 改为同一个值。';

const clearAllTrackersHint = '会清空当前 Tracker 列表中的全部条目，请确认后再执行。';





const sortColumn = ref<keyof Tracker | null>(null);
const sortDirection = ref<'asc' | 'desc'>('asc');

const handleSort = (column: keyof Tracker) => {
  if (sortColumn.value === column) {
    // 已经在此列排序，切换方向或取消排序
    const defaultDir = column === 'enabled' ? 'desc' : 'asc';
    const altDir = column === 'enabled' ? 'asc' : 'desc';

    if (sortDirection.value === defaultDir) {
      sortDirection.value = altDir;
    } else {
      sortColumn.value = null; // 第三次点击回到默认不排序
      sortDirection.value = 'asc';
    }
  } else {
    // 第一次点击该列，'enabled' 默认为倒序（开启的在上），其余为正序
    sortColumn.value = column;
    sortDirection.value = column === 'enabled' ? 'desc' : 'asc';
  }
};

const getSortIcon = (column: keyof Tracker) => {
  if (sortColumn.value !== column) return 'bx bx-sort';
  return sortDirection.value === 'asc' ? 'bx bx-chevron-up' : 'bx bx-chevron-down';
};

const getSortButtonClass = (column: keyof Tracker) => {
  return sortColumn.value === column ? 'is-active' : 'is-idle';
};

const sortedTrackers = computed(() => {
  if (!sortColumn.value) return store.trackers;
  return [...store.trackers].sort((a, b) => {
    let valA: any = a[sortColumn.value!];
    let valB: any = b[sortColumn.value!];

    if (valA === valB) return 0;

    // IP 排序特殊处理（将IP字符串转为可比对的数字）
    if (sortColumn.value === 'ip') {
      const ip2num = (ip: string) => {
        if (!ip) return 0;
        return ip.split('.').reduce((acc, octet) => (acc << 8) + parseInt(octet, 10), 0) >>> 0;
      };
      valA = ip2num(valA as string);
      valB = ip2num(valB as string);
      return sortDirection.value === 'asc' ? (valA > valB ? 1 : -1) : (valA > valB ? -1 : 1);
    }

    if (typeof valA === 'boolean' && typeof valB === 'boolean') {
      valA = valA ? 1 : 0;
      valB = valB ? 1 : 0;
    }

    if (typeof valA === 'string' && typeof valB === 'string') {
        const compareResult = valA.localeCompare(valB, 'zh-CN', { numeric: true });
        return sortDirection.value === 'asc' ? compareResult : -compareResult;
    }

    // fallback compare
    if (valA < valB) return sortDirection.value === 'asc' ? -1 : 1;
    if (valA > valB) return sortDirection.value === 'asc' ? 1 : -1;
    return 0;
  });
});


const newTracker = reactive<TrackerDraft>({
  name: '',
  url: '',
  enabled: true,
});

const batchDomains = ref('');
const batchIpDraft = ref('');

const refreshCloudflareDomains = async (silent = false) => {
  if (!silent) {
    isLoadingCloudflareDomains.value = true;
  }

  try {
    cloudflareDomains.value = await store.loadCloudflareDomains();
  } catch (e: any) {
    const detail = getErrorMessage(e);
    toast.error(`获取 Cloudflare 域名名单失败: ${detail}`);
  } finally {
    isLoadingCloudflareDomains.value = false;
  }
};

onMounted(async () => {
  await Promise.all([
    store.fetchTrackers(),
    refreshCloudflareDomains(true),
  ]);

});


const isValidIpv4 = computed(() => {
  if (!batchIpDraft.value) return false;
  const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  return ipv4Regex.test(batchIpDraft.value.trim());
});





const toggleTracker = async (tracker: Tracker) => {

  try {
    await store.updateTracker(tracker.id, { enabled: !tracker.enabled });
  } catch (e: any) {
    const detail = getErrorMessage(e, '更新失败');
    toast.error(`更新失败: ${detail}`);
    // Revert logic handled in store or need to force refresh
    store.fetchTrackers();
  }
};

const addTrackerDomainToCloudflareList = async (tracker: Tracker) => {
  const domain = normalizeDomain(tracker.url);
  if (!domain) {
    toast.error('当前 Tracker 域名无效，无法加入 Cloudflare 域名名单');
    return;
  }

  if (!await confirm(`确定要将 ${domain} 加入 Cloudflare 域名名单吗？加入后会按 Cloudflare 域名参与识别与优选 IP 应用。`, '加入 Cloudflare 域名名单')) return;
  try {
    await store.includeCloudflareDomain(domain);
    toast.success('已加入 Cloudflare 域名名单');
  } catch (e) {
    toast.error(`添加失败: ${getErrorMessage(e)}`);
  }
};


const confirmDelete = async (tracker: Tracker) => {
  const domain = normalizeDomain(tracker.url) || tracker.url;
  if (await confirm(`确定要删除 ${domain} 吗？`, '删除确认')) {
    try {
      await store.deleteTracker(tracker.id);
      toast.success('删除成功');
    } catch (e: any) {
      const detail = getErrorMessage(e);
      toast.error(`删除失败: ${detail}`);
    }
  }
};

const handleAddTracker = async () => {
  isAddingTracker.value = true;
  try {
    await store.addTracker({ ...newTracker }, forceCloudflare.value);
    isAddTrackerModalOpen.value = false;
    newTracker.name = '';
    newTracker.url = '';
    newTracker.enabled = true;
    forceCloudflare.value = false;
    toast.success('添加成功');
  } catch (e: any) {
    const detail = getErrorMessage(e);
    toast.error(`添加失败: ${detail}`);
  } finally {
    isAddingTracker.value = false;
  }
};

const handleBatchAdd = async () => {
  if (!batchDomains.value.trim()) return;
  isBatchImportingTrackers.value = true;
  try {
    const domains = batchDomains.value.split('\n').map(d => d.trim()).filter(d => d);
    const res = await store.batchImport(domains);
    isBatchImportModalOpen.value = false;
    batchDomains.value = '';
    toast.success(res?.message || '批量添加成功');
  } catch (e: any) {
    const detail = getErrorMessage(e);
    toast.error(`批量添加失败: ${detail}`);
  } finally {
    isBatchImportingTrackers.value = false;
  }
};


const handleBatchUpdateIp = async () => {
  if (!supportsBatchIpUpdate) {
    toast.info(batchIpHint);
    return;
  }
  if (!batchIpDraft.value.trim()) return;
  if (!await confirm(`确定要将当前列表中全部 Tracker 的 IP 修改为 ${batchIpDraft.value} 吗？此操作会批量覆盖现有 IP 记录。`, '批量修改 Tracker IP')) return;
  
  isUpdatingAllTrackerIp.value = true;
  try {
    const result = await store.updateAllTrackersIp(batchIpDraft.value.trim());
    batchIpDraft.value = '';
    toast.success(result?.message || `已批量更新 ${result?.updated ?? 0} 条 Tracker 的当前 IP`);
  } catch (e: any) {
    const detail = getErrorMessage(e);
    toast.error(`批量修改失败: ${detail}`);
  } finally {
    isUpdatingAllTrackerIp.value = false;
  }
};




const handleClearAllTrackers = async () => {
  if (!supportsClearAllTrackers) {
    toast.info(clearAllTrackersHint);
    return;
  }
  if (!await confirm('确定要清空当前 Tracker 列表中的全部条目吗？此操作不可恢复。', '清空 Tracker 列表确认')) return;
  isClearingTrackers.value = true;
  try {
    const result = await store.clearAllTrackers();
    toast.success(result?.message || `已清空 ${result?.cleared ?? 0} 条 Tracker`);
  } catch (e: any) {
    const detail = getErrorMessage(e);
    toast.error(`清空失败: ${detail}`);
  } finally {
    isClearingTrackers.value = false;
  }
};





const handleAddCloudflareDomain = async () => {
  if (!cloudflareDomainDraft.value.trim()) return;
  isAddingCloudflareDomain.value = true;
  try {
    await store.includeCloudflareDomain(cloudflareDomainDraft.value.trim());
    cloudflareDomainDraft.value = '';
    cloudflareDomains.value = await store.loadCloudflareDomains();
    toast.success('已加入 Cloudflare 域名名单');
  } catch (e: any) {
    const detail = getErrorMessage(e);
    toast.error(`添加失败: ${detail}`);
  } finally {
    isAddingCloudflareDomain.value = false;
  }
};

const handleDeleteCloudflareDomain = async (domain: string) => {
  if (!await confirm(`确定要将 ${domain} 从 Cloudflare 域名名单中移除吗？`, '移出 Cloudflare 域名名单')) return;
  try {
    await store.excludeCloudflareDomain(domain);
    cloudflareDomains.value = await store.loadCloudflareDomains();
    toast.success('已从 Cloudflare 域名名单中移除');
  } catch (e: any) {
    const detail = getErrorMessage(e);
    toast.error(`删除 Cloudflare 域名失败: ${detail}`);
  }
};

const getCloudflareTrackerIp = (domain: string): string => {
  const normalizedDomain = normalizeDomain(domain);
  if (!normalizedDomain) return '—';
  const tracker = store.trackers.find(t => normalizeDomain(t.url) === normalizedDomain);
  return tracker?.ip || '未设置';
};
</script>

<style scoped>
.dashboard-redesign {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-height: 0;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.12rem;
}

.page-header-actions {
  display: flex;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.trackers-layout {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  flex: 1 1 auto;
  min-height: 0;
}

.workspace-card {
  min-width: 0;
  border-radius: 1.4rem;
  background: var(--bg-surface);
  border: 1px solid rgba(161, 172, 184, 0.14);
  box-shadow: var(--shadow-sm);
}

.tracker-actions-card,
.trackers-card {
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  min-width: 0;
}

.tracker-actions-card {
  gap: 0.15rem;
}


.workspace-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}


.tracker-card-heading {
  flex: 1 1 240px;
  min-width: 0;
}

.tracker-card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.85rem;
}

.tracker-card-title-row-tabs {
  align-items: flex-start;
  flex-wrap: wrap;
}

.tracker-card-title-row-tabs > div:first-child {
  min-width: 0;
  flex: 1 1 320px;
}

.tracker-view-tabs {
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

.tracker-view-tab {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-width: 10.75rem;
  min-height: 2.6rem;
  padding: 0.62rem 1rem;
  border: 1px solid transparent;
  border-radius: 0.75rem;
  background: transparent;
  color: color-mix(in srgb, var(--text-main) 74%, transparent);
  font-size: 0.9rem;
  font-weight: 700;
  line-height: 1;
  transition: background var(--transition-fast), color var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.tracker-view-tab-main {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.52rem;
  min-width: 0;
}

.tracker-view-tab-main .bx {
  font-size: 1rem;
  flex: 0 0 auto;
  opacity: 0.86;
}

.tracker-view-tab:hover,
.tracker-view-tab:focus-visible {
  color: var(--text-main);
  border-color: rgba(161, 172, 184, 0.14);
  background: rgba(var(--primary-rgb), 0.06);
  box-shadow: 0 0 0 1px rgba(var(--primary-rgb), 0.04);
}

.tracker-view-tab.is-active {
  color: var(--text-heading);
  border-color: rgba(var(--primary-rgb), 0.18);
  background: rgba(var(--primary-rgb), 0.1);
  box-shadow: inset 0 0 0 1px rgba(var(--primary-rgb), 0.08);
}

.tracker-view-tab.is-active .tracker-view-tab-main .bx {
  opacity: 1;
}

@media (max-width: 767px) {
  .tracker-view-tabs {
    width: 100%;
    justify-content: stretch;
    flex-wrap: nowrap;
  }

  .tracker-view-tab {
    flex: 1 1 0;
    min-width: 0;
    padding-inline: 0.75rem;
  }

  .tracker-view-tab-main {
    gap: 0.35rem;
  }

  .tracker-view-tab-main span:last-child {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}



.tracker-cloudflare-tab-content {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
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



.tracker-title-count {
  font-size: 0.88rem;
  font-weight: 600;
  color: rgba(105, 122, 141, 0.72);
}

.workspace-card-header p {
  margin: 0.4rem 0 0;
  color: var(--text-muted);
  line-height: 1.65;
}

.workspace-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  min-width: 5.5rem;
  padding: 0.42rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.workspace-pill-dot {
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
}

.workspace-pill.success {
  color: var(--success-color);
  background: rgba(74, 179, 126, 0.14);
}

.workspace-pill.danger {
  color: var(--danger-color);
  background: rgba(225, 108, 108, 0.14);
}

.tracker-actions-body {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
  min-width: 0;
}

.tracker-actions-top {
  display: block;
}

.tracker-primary-action {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  padding: 1rem 1.1rem;
  border-radius: 1rem;
  border: 1px solid rgba(161, 172, 184, 0.12);
  background: color-mix(in srgb, var(--bg-surface-alt) 72%, transparent);
}

.tracker-primary-action-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.tracker-primary-action-head h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.2;
}


.tracker-status-badge {


  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 1.8rem;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.tracker-status-badge-warning {
  color: #b7791f;
  background: rgba(255, 193, 7, 0.14);
  border: 1px solid rgba(255, 193, 7, 0.2);
}

.tracker-ip-input-group-disabled {
  opacity: 0.76;
}

.tracker-actions-footnote {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.1rem 0.1rem 0;
  color: var(--text-muted);
  font-size: 0.82rem;
  line-height: 1.6;
}

.tracker-actions-footnote i {
  color: #b7791f;
  margin-top: 0.1rem;
  flex: 0 0 auto;
}



.tracker-side-action {
  display: flex;
  align-items: stretch;
}

.tracker-side-button {
  width: 100%;
  min-height: auto;
  justify-content: flex-start;
  gap: 1rem;
  padding: 1.15rem 1.2rem;
  border-radius: 1rem;
  font-size: 0.88rem;
  text-align: left;
}

.tracker-side-icon-wrap {
  width: 2.9rem;
  height: 2.9rem;
  border-radius: 0.95rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  background: rgba(var(--primary-rgb), 0.1);
  color: currentColor;
}

.tracker-side-icon-wrap .bx {
  font-size: 1.2rem;
}

.tracker-side-copy {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 0;
}

.tracker-side-title {
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.2;
}

.tracker-side-desc {
  font-size: 0.84rem;
  color: color-mix(in srgb, currentColor 78%, white 22%);
  line-height: 1.4;
}

.tracker-secondary-actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.tracker-mini-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.48rem;
  min-height: 2.9rem;
  padding: 0.72rem 0.95rem;
  border-radius: 0.95rem;
  border: 1px solid transparent;
  background: var(--bg-surface);
  font-size: 0.85rem;
  font-weight: 600;
  transition: transform var(--transition-base), box-shadow var(--transition-base), border-color var(--transition-base), background-color var(--transition-base);
}


.tracker-mini-action:hover:not(:disabled),
.tracker-mini-action:focus-visible:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.tracker-mini-action:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.tracker-mini-primary {
  color: var(--primary-color);
  background: rgba(var(--primary-rgb), 0.08);
  border-color: rgba(var(--primary-rgb), 0.16);
}

.tracker-mini-info {
  color: #2563eb;
  background: rgba(37, 99, 235, 0.08);
  border-color: rgba(37, 99, 235, 0.16);
}

.tracker-mini-success {
  color: var(--success-color);
  background: rgba(74, 179, 126, 0.08);
  border-color: rgba(74, 179, 126, 0.16);
}

.tracker-mini-warning {
  color: #b7791f;
  background: rgba(255, 193, 7, 0.08);
  border-color: rgba(255, 193, 7, 0.16);
}

.tracker-mini-danger {
  color: var(--danger-color);
  background: rgba(225, 108, 108, 0.08);
  border-color: rgba(225, 108, 108, 0.16);
}

.tracker-ip-editor {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.tracker-ip-editor-compact {
  gap: 0.65rem;
}

.tracker-ip-submit {
  flex: 0 0 auto;
  min-width: 9.75rem;
  border-left: 1px solid rgba(161, 172, 184, 0.14);
}

.tracker-ip-input-group {
  display: flex;
  align-items: stretch;
  min-width: 0;
  overflow: hidden;
  border-radius: 0.95rem;
  border: 1px solid rgba(161, 172, 184, 0.16);
  background: var(--bg-surface);
}

.tracker-ip-prefix {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 0.95rem;
  font-size: 0.82rem;
  font-weight: 700;
  color: rgba(105, 122, 141, 0.78);
  background: color-mix(in srgb, var(--bg-surface-alt) 88%, transparent);
  border-right: 1px solid rgba(161, 172, 184, 0.14);
  white-space: nowrap;
}

.tracker-ip-input {
  border: none;
  border-radius: 0;
  background: transparent;
  min-height: 2.9rem;
  padding-left: 0.9rem;
  padding-right: 0.9rem;
  box-shadow: none !important;
}

.tracker-ip-input:focus {
  box-shadow: none;
}

.tracker-inline-note {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.5;
}

.tracker-inline-note i {
  color: var(--primary-color);
  flex: 0 0 auto;
}

@media (max-width: 900px) {
  .tracker-ip-input-group {
    flex-wrap: wrap;
  }

  .tracker-ip-prefix {
    min-height: 2.75rem;
    border-right: none;
    border-bottom: 1px solid rgba(161, 172, 184, 0.14);
    justify-content: flex-start;
  }

  .tracker-ip-input {
    min-width: 0;
    width: 100%;
  }

  .tracker-ip-submit {
    width: 100%;
    border-left: none;
    border-top: 1px solid rgba(161, 172, 184, 0.14);
    border-radius: 0;
  }

  .tracker-secondary-actions {
    grid-template-columns: 1fr;
  }
}


/* ── Cloudflare 域名名单内联区域 ─────────────────────── */

.tracker-inline-panel {
  margin-top: 0.25rem;
  padding: 1.15rem 1.2rem;
  border-radius: 1.1rem;
  border: 1px solid rgba(161, 172, 184, 0.14);
  background: color-mix(in srgb, var(--bg-surface-alt) 60%, transparent);
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.tracker-inline-panel-cloudflare {
  border-color: rgba(var(--primary-rgb), 0.2);
  background: color-mix(in srgb, rgba(var(--primary-rgb), 0.04) 100%, transparent);
}

.tracker-inline-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.tracker-inline-panel-head h4 {
  margin: 0 0 0.22rem;
  font-size: 0.97rem;
  font-weight: 700;
  color: var(--text-heading);
}

.tracker-inline-panel-head p {
  margin: 0;
  font-size: 0.8rem;
  color: var(--text-muted);
  line-height: 1.5;
}

.tracker-inline-panel-count {
  flex-shrink: 0;
  align-self: flex-start;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
}

.tracker-whitelist-input-row {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
  align-items: center;
}

.tracker-whitelist-input-row-inline {
  flex-wrap: nowrap;
}

@media (max-width: 640px) {
  .tracker-whitelist-input-row-inline {
    flex-wrap: wrap;
  }
}

.tracker-input-group-flex {
  flex: 1 1 160px;
  min-width: 0;
}

.tracker-whitelist-add-btn,
.tracker-cloudflare-refresh-btn {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  white-space: nowrap;
}

.tracker-inline-note-panel {
  padding: 0.6rem 0.75rem;
  border-radius: 0.65rem;
  background: rgba(var(--primary-rgb), 0.055);
}

.tracker-whitelist-state {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.6rem 0.4rem;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.tracker-whitelist-state-empty i {
  font-size: 1.3rem;
  opacity: 0.5;
}

.tracker-cloudflare-table-wrap {
  border: 1px solid rgba(161, 172, 184, 0.14);
  border-radius: 1rem;
  background: var(--bg-surface);
  overflow: hidden;
}

.tracker-cloudflare-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.tracker-cloudflare-table th,
.tracker-cloudflare-table td {
  border-bottom: 1px solid rgba(161, 172, 184, 0.1);
  vertical-align: middle;
}

.tracker-cloudflare-table th:first-child,
.tracker-cloudflare-table td:first-child {
  padding: 12px 12px 12px 16px;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 0;
}

.tracker-cloudflare-domain-cell {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 112px;
  max-width: 100%;
  text-align: center;
}

.tracker-cloudflare-table th:last-child,
.tracker-cloudflare-table td:last-child {
  width: 144px;
  padding: 12px 16px 12px 8px;
  text-align: center;
  white-space: nowrap;
}

.tracker-cloudflare-table td:first-child {
  font-size: 0.9rem;
  color: var(--text-primary);
}

.tracker-cloudflare-table thead th {
  background: color-mix(in srgb, var(--bg-surface-alt) 88%, transparent);
  color: rgba(105, 122, 141, 0.84);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.03em;
}

.tracker-cloudflare-table tbody tr:last-child td {
  border-bottom: none;
}

.tracker-cloudflare-actions {
  display: flex;
  justify-content: center;
}

.tracker-cloudflare-delete-btn {
  min-width: 6.2rem;
}

.tracker-cloudflare-ip-inline {
  display: none;
}

@media (max-width: 640px) {
  .tracker-cloudflare-table,
  .tracker-cloudflare-table thead,
  .tracker-cloudflare-table tbody,
  .tracker-cloudflare-table tr,
  .tracker-cloudflare-table th,
  .tracker-cloudflare-table td {
    display: block;
  }

  .tracker-cloudflare-table thead {
    display: none;
  }

  .tracker-cloudflare-ip-col {
    display: none !important;
  }

  .tracker-cloudflare-ip-inline {
    display: inline;
    margin-left: 0.5rem;
    color: var(--text-muted, #8e9bae);
    font-size: 0.85em;
  }

  .tracker-cloudflare-table tbody tr {
    border-bottom: 1px solid rgba(161, 172, 184, 0.1);
  }

  .tracker-cloudflare-table tbody tr:last-child {
    border-bottom: none;
  }

  .tracker-cloudflare-table td {
    padding: 0.88rem 1rem;
    border-bottom: none;
  }

  .tracker-cloudflare-table td:last-child {
    width: 100%;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    padding-top: 0;
    padding-left: 1rem;
    padding-right: 1rem;
    text-align: right;
  }

  .tracker-cloudflare-table td:first-child {
    max-width: none;
    overflow: visible;
    text-overflow: initial;
    white-space: normal;
  }

  .tracker-cloudflare-domain-cell {
    display: inline;
    max-width: none;
    text-align: left;
    overflow-wrap: anywhere;
    word-break: break-word;
  }

  .tracker-cloudflare-domain,
  .tracker-cloudflare-actions {

    width: 100%;
    text-align: left;
  }

  .tracker-cloudflare-actions {
    padding-top: 0;
    display: flex;
    width: 100%;
    justify-content: flex-end;
    text-align: right;
  }

  .tracker-cloudflare-delete-btn {
    width: auto;
  }
}


.tracker-whitelist-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  max-height: 14rem;
  overflow-y: auto;
}


.tracker-whitelist-list-inline {
  max-height: 10.5rem;
}

.tracker-whitelist-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.42rem 0.75rem;
  border-radius: 0.6rem;
  border: 1px solid rgba(161, 172, 184, 0.12);
  background: var(--bg-surface);
  transition: background 0.15s ease;
}

.tracker-whitelist-item:hover {
  background: color-mix(in srgb, var(--bg-surface-alt) 80%, transparent);
}

.tracker-whitelist-domain {
  font-size: 0.84rem;
  font-family: var(--font-mono, 'SFMono-Regular', Consolas, monospace);
  color: var(--text-primary);
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tracker-whitelist-delete {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.24rem 0.5rem;
  border: none;
  border-radius: 0.5rem;
  background: transparent;
  color: var(--danger-color);
  cursor: pointer;
  opacity: 0.55;
  transition: opacity 0.15s ease, background 0.15s ease;
}

.tracker-whitelist-delete:hover {
  opacity: 1;
  background: rgba(var(--danger-rgb, 225, 108, 108), 0.12);
}



.tracker-modal {
  background: var(--bg-overlay);
}

.tracker-modal-dialog {
  max-width: 45rem;
  padding: 0.85rem;
}

.tracker-modal-content {
  border: 1px solid rgba(161, 172, 184, 0.16);
  border-radius: 1.2rem;
  overflow: hidden;
  background: color-mix(in srgb, var(--bg-surface) 94%, white 6%);
  box-shadow: 0 1.1rem 2.4rem rgba(15, 23, 42, 0.16);
}

.tracker-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 1rem 1.15rem 0.85rem;
  border-bottom: 1px solid var(--divider-color);
  background: linear-gradient(180deg, rgba(var(--primary-rgb), 0.055), transparent 100%);
}

.tracker-modal-title-wrap {
  min-width: 0;
}

.tracker-modal-header .modal-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-heading);
}

.tracker-modal-header p {
  margin: 0.24rem 0 0;
  color: var(--text-muted);
  font-size: 0.84rem;
  line-height: 1.45;
}

.tracker-modal-close {
  flex-shrink: 0;
  margin: 0;
}

.tracker-modal-body {
  padding: 1rem 1.15rem;
}

.tracker-modal-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.tracker-form-panel {
  padding: 0.9rem;
  border: 1px solid rgba(161, 172, 184, 0.14);
  border-radius: 0.95rem;
  background: color-mix(in srgb, var(--bg-surface-alt) 72%, transparent);
}

.tracker-form-panel-main {
  background: linear-gradient(180deg, rgba(var(--primary-rgb), 0.04), transparent 100%);
}

.tracker-form-panel-subtle {
  background: color-mix(in srgb, var(--bg-surface-alt) 58%, transparent);
  padding: 0.68rem 0.82rem;
}

.tracker-form-panel-subtle-embedded {
  margin-top: 0.9rem;
  border-radius: 0.9rem;
  min-height: 2.9rem;
  padding: 0 0.82rem;
  display: flex;
  align-items: center;
}

.tracker-form-panel-info {
  border-color: rgba(37, 99, 235, 0.14);
  background: color-mix(in srgb, rgba(37, 99, 235, 0.08) 100%, transparent);
}

.tracker-form-panel-head {
  margin-bottom: 0.75rem;
}

.tracker-form-panel-head-inline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.tracker-form-panel-head h6 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-heading);
}

.tracker-form-panel-head span {
  display: block;
  margin-top: 0.3rem;
  color: var(--text-muted);
  font-size: 0.81rem;
  line-height: 1.45;
}

.tracker-form-label {
  margin-bottom: 0.48rem;
  color: var(--text-heading);
  font-size: 0.88rem;
  font-weight: 600;
}

.tracker-input-group {
  display: flex;
  align-items: stretch;
  border-radius: 0.9rem;
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: var(--border-color);
}

.tracker-input-group > :deep(.input-group-text) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  min-height: 2.9rem;
  color: var(--primary-color);
  background: color-mix(in srgb, var(--bg-surface-alt) 72%, rgba(var(--primary-rgb), 0.08));
  border: 0;
  border-right: 1px solid var(--border-color);
  border-top-left-radius: 0.9rem !important;
  border-bottom-left-radius: 0.9rem !important;
  border-top-right-radius: 0 !important;
  border-bottom-right-radius: 0 !important;
}

.tracker-input-group > :deep(.form-control) {
  position: relative;
  flex: 1 1 auto;
  width: 1%;
  min-height: 2.9rem;
  border: 0;
  background: var(--bg-surface) !important;
  background-color: var(--bg-surface) !important;
  color: color-mix(in srgb, var(--text-heading) 78%, var(--text-muted));
  box-shadow: none;
  border-top-left-radius: 0 !important;
  border-bottom-left-radius: 0 !important;
  border-top-right-radius: 0.9rem !important;
  border-bottom-right-radius: 0.9rem !important;
}

.tracker-input-group > :deep(.form-control::placeholder) {
  color: color-mix(in srgb, var(--text-muted) 88%, transparent);
}

.tracker-input-group > :deep(.form-control:focus) {
  z-index: 3;
  margin-left: 0;
  box-shadow: inset 0 0 0 1px rgba(var(--primary-rgb), 0.34), 0 0 0 0.2rem rgba(var(--primary-rgb), 0.12);
}

.tracker-input-group-flex {
  flex: 1 1 auto;
}

.tracker-info-note {
  display: flex;
  align-items: center;
  gap: 0.72rem;
}

.tracker-info-note i {
  flex: 0 0 auto;
  color: #3b82f6;
  font-size: 1.1rem;
  align-self: center;
}

.tracker-info-note strong {
  display: block;
  margin-bottom: 0.18rem;
  color: #60a5fa;
  font-size: 0.88rem;
}

.tracker-info-note span {
  color: #60a5fa;
  font-size: 0.8rem;
  line-height: 1.5;
}

.tracker-textarea-shell {
  border: 1px solid var(--border-color);
  border-radius: 0.95rem;
  overflow: hidden;
  background: var(--bg-surface);
}

.tracker-textarea {
  min-height: 16rem;
  resize: vertical;
  border: 0;
  border-radius: 0.95rem !important;
  background: transparent !important;
  color: var(--text-main);
  font-size: 0.83rem;
  line-height: 1.65;
  box-shadow: none !important;
}

.tracker-textarea:focus {
  box-shadow: inset 0 0 0 1px rgba(var(--primary-rgb), 0.34), 0 0 0 0.2rem rgba(var(--primary-rgb), 0.12) !important;
}

.tracker-form-panel-head-compact {
  margin-bottom: 0.6rem;
}

.tracker-whitelist-input-row {
  display: flex;
  align-items: stretch;
  gap: 0.7rem;
}

.tracker-whitelist-add-btn {
  flex: 0 0 auto;
  min-width: 6.25rem;
}

.tracker-whitelist-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  min-height: 6rem;
  border-radius: 0.95rem;
  border: 1px dashed rgba(161, 172, 184, 0.2);
  background: color-mix(in srgb, var(--bg-surface) 88%, transparent);
  color: var(--text-muted);
  font-size: 0.84rem;
}

.tracker-whitelist-state-empty {
  flex-direction: column;
  gap: 0.45rem;
}

.tracker-whitelist-state-empty i {
  font-size: 1.35rem;
  color: color-mix(in srgb, var(--text-muted) 75%, transparent);
}

.tracker-whitelist-list {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.tracker-whitelist-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.72rem 0.82rem;
  border: 1px solid rgba(161, 172, 184, 0.14);
  border-radius: 0.95rem;
  background: color-mix(in srgb, var(--bg-surface) 88%, transparent);
}

.tracker-whitelist-domain {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-heading);
  font-size: 0.84rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

.tracker-whitelist-delete {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: 1px solid rgba(225, 108, 108, 0.18);
  border-radius: 0.7rem;
  background: rgba(225, 108, 108, 0.08);
  color: var(--danger-color);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast), background-color var(--transition-fast), border-color var(--transition-fast);
}

.tracker-whitelist-delete:hover,
.tracker-whitelist-delete:focus-visible {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
  background: rgba(225, 108, 108, 0.12);
  border-color: rgba(225, 108, 108, 0.26);
}

.tracker-switch-stack {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.6rem;
  width: 100%;
}

.tracker-switch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.72rem;
  min-height: 2.9rem;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  margin: 0;
}

.tracker-switch-item-inline {
  min-height: auto;
  padding: 0;
  border: 0;
  background: transparent;
  justify-content: flex-end;
}

.tracker-switch-item .form-check-label {
  color: var(--text-heading);
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
}

.tracker-switch-item .form-check-input {
  width: 2.5rem;
  height: 1.35rem;
  margin: 0;
  cursor: pointer;
  float: none;
  flex-shrink: 0;
  order: 2;
  background-color: rgba(161, 172, 184, 0.3);
  border-color: rgba(161, 172, 184, 0.3);
  box-shadow: none;
}

.tracker-switch-item .form-check-input:checked {
  background-color: rgba(var(--primary-rgb), 0.92);
  border-color: rgba(var(--primary-rgb), 0.92);
}

.tracker-switch-item .form-check-input:focus {
  box-shadow: 0 0 0 0.18rem rgba(var(--primary-rgb), 0.14);
  border-color: rgba(var(--primary-rgb), 0.42);
}

.tracker-modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 0.85rem 1.15rem 1rem;
  border-top: 1px solid var(--divider-color);
  background: color-mix(in srgb, var(--bg-surface-alt) 82%, transparent);
}

.tracker-modal-footer > * {
  margin: 0;
}

.tracker-modal-footer-note {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--text-muted);
  font-size: 0.81rem;
  line-height: 1.5;
}

.tracker-modal-footer-note i {
  color: rgb(var(--primary-rgb));
  font-size: 1rem;
  line-height: 1;
  flex: 0 0 auto;
}

.tracker-modal-footer-note span {
  display: block;
}

.tracker-modal-footer-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.tracker-modal-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.38rem;
  min-height: 2.35rem;
  padding: 0.52rem 0.88rem;
  border: 1px solid transparent;
  border-radius: 0.78rem;
  font-size: 0.86rem;
  font-weight: 600;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast), background-color var(--transition-fast), border-color var(--transition-fast);
}

.tracker-modal-btn:hover:not(:disabled),
.tracker-modal-btn:focus-visible:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.tracker-modal-btn:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.tracker-modal-btn-primary {
  background: linear-gradient(135deg, rgba(var(--primary-rgb), 0.98), rgba(var(--primary-rgb), 0.82));
  color: #fff;
  box-shadow: 0 0.75rem 1.6rem rgba(var(--primary-rgb), 0.22);
}

.tracker-modal-btn-muted {
  background: color-mix(in srgb, var(--bg-surface-alt) 88%, transparent);
  border-color: rgba(161, 172, 184, 0.16);
  color: color-mix(in srgb, var(--text-heading) 74%, var(--text-muted));
}

.tracker-quick-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  border-radius: 0.95rem;
  padding: 0.8rem 1rem;
  font-weight: 600;
  font-size: 0.92rem;
  transition: transform var(--transition-base), box-shadow var(--transition-base), border-color var(--transition-base), background-color var(--transition-base);
}

.action-btn span {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.action-btn-compact {
  padding: 0.58rem 1rem;
  border-radius: 0.8rem;
  font-size: 0.84rem;
  margin-left: 0.25rem;
}

.action-btn-compact:first-child {
  margin-left: 0;
}

.action-btn-compact i {
  font-size: 1rem;
}

.action-btn:hover:not(:disabled),
.action-btn:focus-visible:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.action-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.action-btn-primary {
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
  border-color: rgba(var(--primary-rgb), 0.16);
}

.action-btn-primary:hover:not(:disabled),
.action-btn-primary:focus-visible:not(:disabled) {
  background: rgba(var(--primary-rgb), 0.14);
  border-color: rgba(var(--primary-rgb), 0.28);
}

.action-tile {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  width: 100%;
  min-width: 0;
  padding: 1rem 1.05rem;
  border-radius: 1rem;
  border: 1px solid transparent;
  background: color-mix(in srgb, var(--bg-surface-alt) 82%, transparent);
  text-align: left;
  transition: transform var(--transition-base), box-shadow var(--transition-base), border-color var(--transition-base), background-color var(--transition-base);
}

.action-tile i {
  flex-shrink: 0;
  font-size: 1.3rem;
}

.action-tile div {
  min-width: 0;
}

.action-tile strong,
.action-tile span {
  display: block;
}

.action-tile strong {
  font-size: 0.95rem;
  font-weight: 700;
  color: inherit;
}

.action-tile span {
  margin-top: 0.2rem;
  font-size: 0.78rem;
  line-height: 1.5;
  color: var(--text-muted);
}

.action-tile:hover:not(:disabled),
.action-tile:focus-visible:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.action-tile:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.action-tile-primary {
  color: var(--primary-color);
  background: rgba(var(--primary-rgb), 0.08);
  border-color: rgba(var(--primary-rgb), 0.16);
}

.action-tile-info {
  color: #2563eb;
  background: rgba(37, 99, 235, 0.08);
  border-color: rgba(37, 99, 235, 0.16);
}

.action-tile-success {
  color: var(--success-color);
  background: rgba(74, 179, 126, 0.08);
  border-color: rgba(74, 179, 126, 0.16);
}

.action-tile-warning {
  color: #b7791f;
  background: rgba(255, 193, 7, 0.08);
  border-color: rgba(255, 193, 7, 0.16);
}

.action-tile-danger {
  color: var(--danger-color);
  background: rgba(225, 108, 108, 0.08);
  border-color: rgba(225, 108, 108, 0.16);
}

.trackers-content-area {
  min-width: 0;
}

.workspace-empty {
  min-height: 24rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: var(--text-muted);
  text-align: center;
}

.workspace-empty i {
  font-size: 2.2rem;
}

.workspace-empty strong {
  color: var(--text-heading);
  font-size: 1rem;
}

.trackers-loading .spinner-border {
  width: 2rem;
  height: 2rem;
}

.tracker-table {
  border: 1px solid rgba(161, 172, 184, 0.12);
  border-radius: 1rem;
  overflow: hidden;
  background: color-mix(in srgb, var(--bg-surface-alt) 72%, transparent);
}

.tracker-table-header,
.tracker-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr) minmax(11rem, 1fr);
  column-gap: 0.6rem;
  align-items: center;
}

.tracker-table-header {
  padding: 0.62rem 0.9rem;
  border-bottom: 1px solid rgba(161, 172, 184, 0.12);
  background: color-mix(in srgb, var(--bg-surface) 86%, transparent);
}

.tracker-sort-btn,
.tracker-table-action-label {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-width: 0;
  border: none;
  padding: 0.28rem 0.55rem;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-align: left;
}

.tracker-sort-btn {
  justify-content: flex-start;
  justify-self: start;
  width: auto;
  max-width: 100%;
  border-radius: 999px;
  transition: background-color var(--transition-base), color var(--transition-base), box-shadow var(--transition-base), transform var(--transition-base);
}

.tracker-sort-btn:hover,
.tracker-sort-btn:focus-visible {
  color: var(--text-heading);
  background: rgba(var(--primary-rgb), 0.08);
}

.tracker-sort-btn.is-active {
  color: var(--primary-color);
  background: rgba(var(--primary-rgb), 0.12);
  box-shadow: inset 0 0 0 1px rgba(var(--primary-rgb), 0.12);
}

.tracker-sort-label {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tracker-sort-indicator {
  width: 1.2rem;
  height: 1.2rem;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  background: rgba(161, 172, 184, 0.14);
  color: inherit;
  font-size: 0.8rem;
}

.tracker-sort-btn.is-active .tracker-sort-indicator {
  background: rgba(var(--primary-rgb), 0.16);
}

.tracker-sort-btn-center,
.tracker-table-action-label {
  justify-content: center;
}

.tracker-sort-btn-center {
  justify-self: center;
}

.tracker-table-body {
  display: flex;
  flex-direction: column;
}

.tracker-row {
  padding: 0.56rem 0.9rem;
  border-bottom: 1px solid rgba(161, 172, 184, 0.12);
  transition: background-color var(--transition-base);
}

.tracker-row:last-child {
  border-bottom: none;
}

.tracker-row:hover {
  background: rgba(161, 172, 184, 0.06);
}

.tracker-col-name,
.tracker-col-network,
.tracker-col-domain,
.tracker-col-ip,
.tracker-col-switch,
.tracker-col-actions {
  min-width: 0;
}

.tracker-col-name strong {
  display: block;
  color: var(--text-heading);
  font-size: 0.86rem;
  font-weight: 700;
  white-space: nowrap;
}

.tracker-col-network {
  display: contents;
}

.tracker-col-domain,
.tracker-col-ip {
  color: var(--text-heading);
  font-size: 0.78rem;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tracker-col-switch {
  display: flex;
  align-items: center;
  justify-content: center;
}

.tracker-switch {
  flex-shrink: 0;
}

.tracker-col-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.tracker-action-btn {
  flex: 1 1 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  border-radius: 0.78rem;
  min-height: 1.9rem;
  padding: 0.38rem 0.58rem;
  font-size: 0.78rem;
  font-weight: 600;
  transition: transform var(--transition-base), box-shadow var(--transition-base), border-color var(--transition-base), background-color var(--transition-base);
}

.tracker-action-btn span {
  display: inline-flex;
  align-items: center;
  gap: 0.32rem;
  white-space: nowrap;
}

.tracker-action-btn:hover:not(:disabled),
.tracker-action-btn:focus-visible:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.tracker-action-success {
  background: rgba(74, 179, 126, 0.1);
  color: var(--success-color);
  border-color: rgba(74, 179, 126, 0.16);
}

.tracker-action-success:hover:not(:disabled),
.tracker-action-success:focus-visible:not(:disabled) {
  background: rgba(74, 179, 126, 0.14);
  border-color: rgba(74, 179, 126, 0.28);
}

.tracker-action-danger {
  background: rgba(225, 108, 108, 0.1);
  color: var(--danger-color);
  border-color: rgba(225, 108, 108, 0.16);
}

.tracker-action-danger:hover:not(:disabled),
.tracker-action-danger:focus-visible:not(:disabled) {
  background: rgba(225, 108, 108, 0.14);
  border-color: rgba(225, 108, 108, 0.28);
}

.switch {
  --switch-width: 46px;
  --switch-height: 24px;
  --switch-bg: rgba(161, 172, 184, 0.42);
  --switch-checked-bg: linear-gradient(135deg, color-mix(in srgb, var(--success-color) 86%, #3dd598) 0%, var(--success-color) 100%);
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
  --icon-checkmark-color: var(--success-color);
  --icon-checkmark-size: 10px;
  --effect-width: calc(var(--circle-diameter) / 2);
  --effect-height: calc(var(--effect-width) / 2 - 1px);
  --effect-bg: var(--circle-bg);
  --effect-border-radius: 1px;
  --effect-transition: all .2s ease-in-out;
  display: inline-block;
}

.switch input {
  display: none;
}

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

.slider::before {
  content: "";
  position: absolute;
  width: var(--effect-width);
  height: var(--effect-height);
  top: 50%;
  left: calc(var(--switch-offset) + (var(--effect-width) / 2));
  background: var(--effect-bg);
  border-radius: var(--effect-border-radius);
  transition: var(--effect-transition);
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

.switch input:checked + .slider::before {
  left: calc(100% - var(--effect-width) - (var(--effect-width) / 2) - var(--switch-offset));
}

.switch input:checked + .slider .circle {
  left: calc(100% - var(--circle-diameter) - var(--switch-offset));
  box-shadow: var(--circle-checked-shadow);
}

@media (max-width: 991.98px) {
  .tracker-actions-top {
    grid-template-columns: 1fr;
  }

  .tracker-secondary-actions {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .tracker-table-header {
    display: none;
  }

  .tracker-row {
    grid-template-columns: minmax(0, 1fr) auto;
    grid-template-areas:
      "name toggle"
      "network network"
      "actions actions";
    gap: 0.8rem;
    padding: 1rem 0.55rem;
  }

  .tracker-col-name {
    grid-area: name;
  }

  .tracker-col-network {
    grid-area: network;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 0.45rem;
    min-width: 0;
  }

  .tracker-col-domain {
    width: auto;
    max-width: min(100%, 13rem);
    padding-right: 0;
    flex: 0 1 auto;
  }

  .tracker-col-ip {
    width: auto;
    text-align: left;
    flex: 0 0 auto;
  }

  .tracker-col-switch {
    grid-area: toggle;
    justify-self: end;
  }

  .tracker-col-actions {
    grid-area: actions;
  }
}

@media (max-width: 767.98px) {
  .tracker-actions-card,
  .trackers-card {
    padding: 1rem;
  }

  .tracker-modal-dialog {
    padding: 0.5rem;
  }

  .tracker-modal-header,
  .tracker-modal-body,
  .tracker-modal-footer {
    padding-left: 0.95rem;
    padding-right: 0.95rem;
  }

  .tracker-form-panel-head-inline {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    flex-wrap: nowrap;
  }

  .tracker-info-note {
    align-items: flex-start;
  }

  .tracker-info-note i {
    align-self: flex-start;
    margin-top: 0.08rem;
  }

  .tracker-modal-footer {
    align-items: stretch;
    flex-direction: column;
  }

  .tracker-modal-footer-note {
    width: 100%;
    text-align: center;
  }

  .tracker-modal-footer-actions {
    width: 100%;
    margin: 0 auto;
    justify-content: center;
    align-items: center;
  }

  .tracker-modal-btn,
  .tracker-modal-footer-actions .tracker-modal-btn {
    flex: 1 1 0;
    justify-content: center;
  }

  .tracker-whitelist-input-row {
    flex-direction: column;
  }

  .tracker-whitelist-input-row-inline {
    flex-direction: column;
    align-items: stretch;
  }

  .tracker-whitelist-input-row-inline .tracker-input-group-flex {
    width: 100%;
  }

  .tracker-whitelist-input-row-inline .tracker-whitelist-add-btn,
  .tracker-whitelist-input-row-inline .tracker-cloudflare-refresh-btn {
    flex: 1 1 0;
    width: auto;
    min-width: 0;
    padding-inline: 0.7rem;
    font-size: 0.82rem;
    gap: 0.28rem;
  }

  .tracker-whitelist-input-row-inline .tracker-cloudflare-refresh-btn {
    justify-content: center;
  }

  .tracker-whitelist-input-row-inline .tracker-whitelist-add-btn + .tracker-cloudflare-refresh-btn {
    margin-top: 0;
  }

  .tracker-whitelist-input-row-inline .tracker-whitelist-add-btn,
  .tracker-whitelist-input-row-inline .tracker-cloudflare-refresh-btn {
    width: 100%;
  }

  .tracker-whitelist-input-row-inline .tracker-whitelist-add-btn,
  .tracker-whitelist-input-row-inline .tracker-cloudflare-refresh-btn {
    max-width: none;
  }

  .tracker-whitelist-input-row-inline:has(.tracker-whitelist-add-btn) {
    gap: 0.7rem;
  }

  .tracker-whitelist-input-row-inline {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .tracker-whitelist-input-row-inline .tracker-input-group-flex {
    grid-column: 1 / -1;
  }

  .tracker-whitelist-add-btn {
    width: 100%;
  }

  .tracker-whitelist-item {
    padding: 0.68rem 0.74rem;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .page-header-actions {
    width: 100%;
    order: 3;
  }

  .action-btn {
    flex: 1 1 0;
  }

  .tracker-secondary-actions {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    justify-content: stretch;
  }

  .tracker-secondary-actions .tracker-mini-danger {
    grid-column: 1 / -1;
  }

  .tracker-side-button {
    justify-content: flex-start;
  }

  .tracker-ip-input-group {
    flex-direction: column;
    border-radius: 1rem;
    overflow: hidden;
  }

  .tracker-mini-action {
    justify-content: center;
    width: 100%;
    min-height: 3rem;
    padding-inline: 0.7rem;
    font-size: 0.82rem;
    gap: 0.35rem;
  }

  .tracker-ip-submit {
    margin-left: 0;
  }

  .tracker-ip-prefix {
    justify-content: flex-start;
    padding: 0.8rem 1rem 0.55rem;
    border-right: none;
    border-bottom: 1px solid rgba(161, 172, 184, 0.16);
  }

  .tracker-table {
    border-radius: 1rem;
    border-left: 1px solid rgba(161, 172, 184, 0.12);
    border-right: 1px solid rgba(161, 172, 184, 0.12);
  }

  .tracker-table-header {
    display: none;
  }

  .tracker-row {
    grid-template-columns: minmax(0, 1fr) auto;
    grid-template-areas:
      "name toggle"
      "network network"
      "actions actions";
    gap: 0.8rem;
    padding: 1rem 0.55rem;
  }

  .tracker-col-name {
    grid-area: name;
  }

  .tracker-col-network {
    grid-area: network;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 0.45rem;
    min-width: 0;
  }

  .tracker-col-domain {
    width: auto;
    max-width: min(100%, 13rem);
    padding-right: 0;
    flex: 0 1 auto;
  }

  .tracker-col-ip {
    width: auto;
    text-align: left;
    flex: 0 0 auto;
  }

  .tracker-col-switch {
    grid-area: toggle;
    justify-self: end;
  }

  .tracker-col-actions {
    grid-area: actions;
    width: 100%;
    justify-content: flex-end;
  }

  .tracker-action-btn {
    flex: 0 0 auto;
  }
}
</style>
