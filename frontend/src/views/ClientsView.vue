<template>
  <div class="dashboard-redesign">
    <PageHeaderShell title="下载器管理" :is-mobile="isMobile">
      <template #actions>
        <button class="action-btn action-btn-success action-btn-compact" @click="handleImportTrackers" :disabled="importing" title="从已启用下载器扫描 Tracker，并汇总导入结果">
          <span>
            <span v-if="importing" class="spinner-border spinner-border-sm"></span>
            <i v-else class="bx bx-cloud-download"></i>
            <span v-if="!isMobile">导入Tracker</span>
          </span>
        </button>
        <button class="action-btn action-btn-primary action-btn-compact" @click="openAddModal">
          <span>
            <i class="bx bx-plus-circle"></i>
            <span v-if="!isMobile">添加下载器</span>
          </span>
        </button>
      </template>
    </PageHeaderShell>

    <section class="clients-layout">
      <article class="workspace-card clients-card">
        <header class="workspace-card-header clients-card-header">
          <div class="clients-card-heading">
            <div class="clients-card-title-row">
              <h3>配置列表</h3>
              <span class="workspace-pill" :class="store.clients.length ? 'success' : 'danger'">
                <span class="workspace-pill-dot"></span>
                {{ store.clients.length ? `${store.clients.length} CLIENTS` : 'EMPTY' }}
              </span>
            </div>
            <p>集中管理 qBittorrent、Transmission 下载器连接信息，并支持导入 Tracker、查看导入摘要与联机测试。</p>
          </div>
        </header>

        <div class="clients-content">
          <section v-if="lastImportResult" class="import-result-panel" :class="lastImportResult.imported > 0 ? 'is-success' : 'is-neutral'">
            <div class="import-result-head">
              <div>
                <div class="import-result-title-row">
                  <h4>最近一次导入结果</h4>
                  <span class="import-result-badge" :class="lastImportResult.imported > 0 ? 'success' : 'neutral'">
                    {{ importResultBadgeText }}
                  </span>
                </div>
                <p>{{ lastImportResult.message || '导入完成' }}</p>
              </div>
              <button type="button" class="import-result-dismiss" @click="lastImportResult = null" aria-label="关闭导入结果面板">
                <i class="bx bx-x"></i>
              </button>
            </div>

            <div class="import-result-stats">
              <article class="import-result-stat-card import-result-stat-highlight">
                <span>新增导入</span>
                <strong>{{ lastImportResult.imported }}</strong>
                <small>本轮成功写入的 Cloudflare Tracker 数量</small>
              </article>
              <article class="import-result-stat-card">
                <span>重复跳过</span>
                <strong>{{ lastImportResult.skipped }}</strong>
                <small>已存在或无需重复导入的目标</small>
              </article>
              <article class="import-result-stat-card">
                <span>唯一目标</span>
                <strong>{{ lastImportResult.unique_tracker_count }}</strong>
                <small>从下载器汇总后的去重结果</small>
              </article>
              <article class="import-result-stat-card">
                <span>扫描范围</span>
                <strong>{{ lastImportResult.tracker_count }}</strong>
                <small>{{ lastImportResult.torrent_count }} 个下载器侧唯一目标参与统计</small>
              </article>
            </div>

            <div class="import-result-grid">
              <article class="import-result-block import-result-block-success">
                <div class="import-result-block-head">
                  <div>
                    <h5>Cloudflare 命中</h5>
                    <p>这些目标已进入本轮导入判断。</p>
                  </div>
                  <span class="import-result-count">{{ lastImportResult.cloudflare_domains.length }}</span>
                </div>
                <div v-if="lastImportResult.cloudflare_domains.length" class="import-result-chip-list">
                  <span v-for="domain in visibleCloudflareDomains" :key="domain" class="import-result-chip import-result-chip-success">{{ domain }}</span>
                </div>
                <div v-else class="import-result-empty">本轮没有命中 Cloudflare 的 Tracker 目标。</div>
                <button
                  v-if="lastImportResult.cloudflare_domains.length > IMPORT_RESULT_PREVIEW_LIMIT"
                  type="button"
                  class="import-result-link"
                  @click="showAllCloudflareDomains = !showAllCloudflareDomains"
                >
                  {{ showAllCloudflareDomains ? '收起 Cloudflare 列表' : `展开剩余 ${lastImportResult.cloudflare_domains.length - IMPORT_RESULT_PREVIEW_LIMIT} 个 Cloudflare 目标` }}
                </button>
              </article>

              <article class="import-result-block import-result-block-muted">
                <div class="import-result-block-head">
                  <div>
                    <h5>未命中 Cloudflare</h5>
                    <p>这些目标已扫描，但不会写入当前 Tracker 列表。</p>
                  </div>
                  <span class="import-result-count">{{ lastImportResult.non_cloudflare_domains.length }}</span>
                </div>
                <div v-if="lastImportResult.non_cloudflare_domains.length" class="import-result-chip-list">
                  <span v-for="domain in visibleNonCloudflareDomains" :key="domain" class="import-result-chip">{{ domain }}</span>
                </div>
                <div v-else class="import-result-empty">本轮没有未命中 Cloudflare 的目标。</div>
                <button
                  v-if="lastImportResult.non_cloudflare_domains.length > IMPORT_RESULT_PREVIEW_LIMIT"
                  type="button"
                  class="import-result-link"
                  @click="showAllNonCloudflareDomains = !showAllNonCloudflareDomains"
                >
                  {{ showAllNonCloudflareDomains ? '收起未命中列表' : `展开剩余 ${lastImportResult.non_cloudflare_domains.length - IMPORT_RESULT_PREVIEW_LIMIT} 个未命中目标` }}
                </button>
              </article>
            </div>

            <article v-if="importClientSummaryItems.length" class="import-result-block import-result-block-summary">
              <div class="import-result-block-head">
                <div>
                  <h5>下载器扫描明细</h5>
                  <p>逐个查看本轮从哪些下载器读到了目标，哪些下载器连接失败。</p>
                </div>
                <span class="import-result-count">{{ importClientSummaryItems.length }}</span>
              </div>
              <div class="import-result-summary-list">
                <div v-for="item in importClientSummaryItems" :key="item" class="import-result-summary-item">
                  <i class="bx bx-data"></i>
                  <span>{{ item }}</span>
                </div>
              </div>
            </article>
          </section>

          <PageEmptyState
            v-if="store.loading"
            container-class="clients-loading"
            loading
            description="正在加载下载器配置..."
          />

          <PageEmptyState
            v-else-if="store.clients.length === 0"
            container-class="clients-empty"
            title="暂无下载器配置"
            description="点击右上角“添加下载器”开始配置客户端连接。"
          />

          <div v-else class="client-grid">
            <article class="client-card" v-for="client in store.clients" :key="client.id">
              <div class="client-card-top">
                <div class="client-title-block">
                  <div class="client-title-line">
                    <h4>{{ client.name }}</h4>
                    <div class="client-badges">
                      <span class="client-badge" :class="getTypeBadgeClass(client.type)">{{ getTypeNameShort(client.type) }}</span>
                      <span v-if="client.version" class="client-badge client-version" :class="getTypeBadgeClass(client.type)">{{ client.version }}</span>
                      <span class="client-badge" :class="client.enable ? 'badge-enabled' : 'badge-disabled'">
                        {{ client.enable ? '已启用' : '已禁用' }}
                      </span>
                    </div>
                </div>
                  <p>{{ client.host }}</p>
                </div>
              </div>

              <div class="client-meta-list">
                <div class="client-meta-item">
                  <span>客户端类型</span>
                  <strong>{{ getTypeName(client.type) }}</strong>
                </div>
                <div class="client-meta-item">
                  <span>登录用户</span>
                  <strong>{{ client.username || '未设置' }}</strong>
                </div>
              </div>

              <div class="client-card-actions">
                <button class="client-action-btn client-action-success" @click="testConnection(client.id)" :disabled="testing === client.id">
                  <span>
                    <span v-if="testing === client.id" class="spinner-border spinner-border-sm"></span>
                    <template v-else>
                      <i class="bx bx-check-circle"></i>
                      <span>测试</span>
                    </template>
                  </span>
                </button>
                <button class="client-action-btn client-action-primary" @click="openEditModal(client)">
                  <span>
                    <i class="bx bx-pencil"></i>
                    <span>编辑</span>
                  </span>
                </button>
                <button class="client-action-btn client-action-danger" @click="confirmDelete(client)">
                  <span>
                    <i class="bx bx-trash"></i>
                    <span>删除</span>
                  </span>
                </button>
              </div>
            </article>
          </div>
        </div>
      </article>
    </section>

    <!-- Edit Modal -->
    <div v-if="showModal" class="modal fade show d-block client-modal" @click.self="showModal = false">
      <div class="modal-dialog modal-lg modal-dialog-centered client-modal-dialog">
        <div class="modal-content client-modal-content">
          <div class="modal-header client-modal-header">
            <div class="client-modal-title-wrap">
              <h5 class="modal-title">{{ isEdit ? '编辑' : '添加' }}下载器</h5>
              <p>填写连接信息后即可测试并保存。</p>
            </div>
            <button type="button" class="btn-close client-modal-close" @click="showModal = false"></button>
          </div>
          <div class="modal-body client-modal-body">
            <form @submit.prevent="handleSaveClient" class="client-modal-form">
              <section class="client-form-panel client-form-panel-main">
                <div class="client-form-panel-head client-form-panel-head-inline">
                  <h6>连接配置</h6>
                  <div class="form-check form-switch client-switch-item client-switch-item-inline">
                    <input class="form-check-input" type="checkbox" id="client-enable" v-model="form.enable">
                    <label class="form-check-label" for="client-enable">启用</label>
                  </div>
                </div>

                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label client-form-label">客户端名称 <span class="text-danger">*</span></label>
                    <div class="input-group client-input-group">
                      <span class="input-group-text"><i class="bx bx-purchase-tag-alt"></i></span>
                      <input type="text" class="form-control" v-model="form.name" required placeholder="如：qBittorrent">
                    </div>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label client-form-label">下载器类型 <span class="text-danger">*</span></label>
                    <div ref="typeWrapperRef" class="client-type-wrapper position-relative">
                    <div class="input-group client-input-group client-type-group" :class="{ 'is-disabled': isEdit }">
                      <span class="input-group-text"><i class="bx bx-network-chart"></i></span>
                      <button
                        type="button"
                        class="form-control client-type-trigger"
                        :disabled="isEdit"
                        @click="toggleTypeDropdown"
                      >
                        <span :class="{ 'is-placeholder': !form.type }">{{ selectedTypeLabel }}</span>
                        <i class="bx bx-chevron-down" :class="{ 'is-open': typeDropdownOpen }"></i>
                      </button>
                    </div>

                    <transition name="cron-dropdown">
                      <div v-if="typeDropdownOpen && !isEdit" class="client-type-dropdown">
                        <div class="client-protocol-dropdown-note client-type-dropdown-note">
                          <strong>下载器类型</strong>
                          <span>选择后会自动带入默认端口，并匹配对应连接方式。</span>
                        </div>
                        <button
                          v-for="type in store.supportedTypes"
                          :key="type.type"
                          type="button"
                          class="client-protocol-option client-type-option"
                          :class="{ 'is-active': form.type === type.type }"
                          @click="selectClientType(type.type)"
                        >
                          <strong>{{ type.name }}</strong>
                          <span>{{ type.type }}</span>
                        </button>
                      </div>
                    </transition>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label client-form-label">主机地址 <span class="text-danger">*</span></label>
                    <div ref="hostWrapperRef" class="client-host-wrapper position-relative">
                      <div class="input-group client-input-group client-host-group" @click="handleHostGroupClick">
                        <span class="input-group-text"><i class="bx bx-desktop"></i></span>
                        <input
                          ref="hostInputRef"
                          type="text"
                          class="form-control client-host-input"
                          :value="hostInputValue"
                          required
                          placeholder=""
                          @focus="openProtocolDropdown"
                          @input="handleHostInput"
                        >
                        <button
                          type="button"
                          class="client-host-clear-btn"
                          v-if="form.host"
                          @click.stop="clearHostInput"
                          title="清空"
                        >
                          <i class="bx bx-x"></i>
                        </button>
                        <button
                          type="button"
                          class="client-protocol-trigger"
                          :class="{ 'is-open': protocolDropdownOpen }"
                          @click.stop="toggleProtocolDropdown"
                          aria-label="选择协议"
                          tabindex="-1"
                          aria-hidden="true"
                        >
                          <span>{{ selectedProtocolLabel }}</span>
                        </button>
                      </div>

                      <transition name="cron-dropdown">
                        <div v-if="protocolDropdownOpen" class="client-protocol-dropdown">
                          <div class="client-protocol-dropdown-note">
                            <strong>协议说明</strong>
                            <span>可直接输入完整地址，或先选择协议再填写主机。</span>
                          </div>
                          <button
                            v-for="option in protocolOptions"
                            :key="option.value"
                            type="button"
                            class="client-protocol-option"
                            :class="{ 'is-active': currentProtocol === option.value }"
                            @click="selectProtocol(option.value)"
                          >
                            <strong>{{ option.label }}</strong>
                            <span>{{ option.prefix }}</span>
                          </button>
                        </div>
                      </transition>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label client-form-label">端口 <span class="text-danger">*</span></label>
                    <div class="input-group client-input-group">
                      <span class="input-group-text"><i class="bx bx-hash"></i></span>
                      <input type="number" class="form-control" v-model="form.port" required placeholder="8080" @input="portTouched = true">

                    </div>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label client-form-label">用户名</label>
                    <div class="input-group client-input-group">
                      <span class="input-group-text"><i class="bx bx-user"></i></span>
                      <input type="text" class="form-control" v-model="form.username" placeholder="可选">
                    </div>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label client-form-label">密码</label>
                    <div class="input-group client-input-group">
                      <span class="input-group-text"><i class="bx bx-key"></i></span>
                      <input type="password" class="form-control" v-model="form.password" placeholder="可选">
                    </div>
                  </div>
                  <div class="col-12" v-if="form.type === 'qbittorrent'">
                    <label class="form-label client-form-label">API Key</label>
                    <div class="input-group client-input-group">
                      <span class="input-group-text"><i class="bx bx-shield-quarter"></i></span>
                      <input type="password" class="form-control" v-model="form.apikey" placeholder="qBittorrent 5.2+ 可选，优先于用户名密码">
                    </div>
                  </div>
                </div>
              </section>
            </form>
          </div>
          <div class="modal-footer client-modal-footer">
            <button type="button" class="client-modal-btn client-modal-btn-ghost" @click="testConfig" :disabled="testingConfig">
              <span v-if="testingConfig" class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bx bx-wifi"></i>
              <span>测试连接</span>
            </button>
            <div class="client-modal-footer-actions">
              <button type="button" class="client-modal-btn client-modal-btn-muted" @click="showModal = false">取消</button>
              <button type="button" class="client-modal-btn client-modal-btn-primary" @click="handleSaveClient" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bx bx-save"></i>
                <span>保存配置</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue';
import { useClientStore, type TorrentClient, type Downloader } from '@/stores/modules/clients';
import type { ImportTrackersResult } from '@/api/clients';
import { useMobile } from '@/composables/useMobile';
import { useToast } from '@/composables/useToast';
import { useConfirm } from '@/composables/useConfirm';
import PageEmptyState from '@/components/shared/PageEmptyState.vue';
import PageHeaderShell from '@/components/shared/PageHeaderShell.vue';
import { getErrorMessage } from '@/utils/error';


const store = useClientStore();
const { isMobile } = useMobile();
const toast = useToast();
const { confirm } = useConfirm();
const showModal = ref(false);
const isEdit = ref(false);
const importing = ref(false);
const originalPassword = ref('');
const originalApiKey = ref('');
const testing = ref<string | null>(null);
const testingConfig = ref(false);
const saving = ref(false);
const protocolDropdownOpen = ref(false);
const typeDropdownOpen = ref(false);
const portTouched = ref(false);
const hostWrapperRef = ref<HTMLElement | null>(null);
const typeWrapperRef = ref<HTMLElement | null>(null);
const hostInputRef = ref<HTMLInputElement | null>(null);
const hostInputValue = ref('');
const lastImportResult = ref<ImportTrackersResult | null>(null);
const showAllCloudflareDomains = ref(false);
const showAllNonCloudflareDomains = ref(false);

const IMPORT_RESULT_PREVIEW_LIMIT = 8;


const protocolOptions = [
  { value: 'http', label: 'HTTP', prefix: 'http://' },
  { value: 'https', label: 'HTTPS', prefix: 'https://' }
] as const;

const form = reactive<TorrentClient>({
  id: '',
  name: '',
  type: '',
  host: 'localhost',
  port: 8080,
  username: '',
  password: '',
  apikey: '',
  enabled: true,
  enable: true,
});

// host 字段直接包含完整地址，格式如：https://qbittorrent.example.com:8099
const currentProtocol = computed(() => {
  const h = form.host.toLowerCase();
  if (h.startsWith('https://')) return 'https';
  if (h.startsWith('http://')) return 'http';
  return 'http';
});

const selectedTypeLabel = computed(() => {
  if (!form.type) return '选择类型';
  const target = store.supportedTypes.find(type => type.type === form.type);
  return target?.name || form.type;
});

// 当前协议标签显示
const selectedProtocolLabel = computed(() => {
  return currentProtocol.value.toUpperCase();
});

// 同步 hostInputValue（用于显示输入框中的完整地址）
const syncHostInputValue = () => {
  hostInputValue.value = form.host || '';
};

// 从完整地址中提取 host（去掉协议）
const extractHost = (value: string): string => {
  const lower = value.toLowerCase();
  if (lower.startsWith('https://')) return value.substring(8);
  if (lower.startsWith('http://')) return value.substring(7);
  return value;
};

// 从完整地址中提取端口（如果 host 中没有端口，返回 -1 表示不覆盖）
const extractPort = (value: string): number => {
  const host = extractHost(value);
  const portMatch = host.match(/:(\d+)$/);
  if (portMatch && portMatch[1]) {
    return parseInt(portMatch[1], 10);
  }
  return -1; // 返回 -1 表示 host 中没有端口，不应覆盖现有端口
};

// 从完整地址中提取纯 host（去掉端口）
const extractCleanHost = (value: string): string => {
  const host = extractHost(value);
  return host.replace(/:\d+$/, '');
};

const normalizeHostInput = (value: string) => {
  const trimmed = value.trim();
  if (!trimmed) {
    form.host = '';
    return;
  }
  // 保持 host 字段为完整地址（包含协议和端口）
  form.host = trimmed;
  // 如果 host 中包含端口，则提取并更新端口
  const extractedPort = extractPort(trimmed);
  if (extractedPort !== -1) {
    form.port = extractedPort;
  }
  // 如果 host 不含端口，保持 form.port 不变（保留用户手动输入的值）
};

const openProtocolDropdown = () => {
  protocolDropdownOpen.value = true;
};

const toggleProtocolDropdown = () => {
  protocolDropdownOpen.value = !protocolDropdownOpen.value;
  if (protocolDropdownOpen.value) {
    typeDropdownOpen.value = false;
    hostInputRef.value?.focus();
  }
};

const toggleTypeDropdown = () => {
  if (isEdit.value) return;
  typeDropdownOpen.value = !typeDropdownOpen.value;
  if (typeDropdownOpen.value) {
    protocolDropdownOpen.value = false;
  }
};

const handleHostGroupClick = () => {
  typeDropdownOpen.value = false;
  hostInputRef.value?.focus();
  openProtocolDropdown();
};

const handleHostInput = (event: Event) => {
  const value = (event.target as HTMLInputElement).value;
  hostInputValue.value = value;
  normalizeHostInput(value);
  protocolDropdownOpen.value = true;
};

const clearHostInput = () => {
  form.host = '';
  hostInputValue.value = '';
  typeDropdownOpen.value = false;
  protocolDropdownOpen.value = true;
  hostInputRef.value?.focus();
};

const selectClientType = (type: string) => {
  form.type = type;
  onTypeChange();
  typeDropdownOpen.value = false;
};

const selectProtocol = (protocol: 'http' | 'https') => {
  // 更新 host 中的协议
  const currentHost = form.host || '';
  const cleanHost = extractCleanHost(currentHost) || 'localhost';
  form.host = `${protocol}://${cleanHost}`;
  syncHostInputValue();
  protocolDropdownOpen.value = false;
  hostInputRef.value?.focus();
};

const handleProtocolClickOutside = (event: MouseEvent) => {
  if (!hostWrapperRef.value?.contains(event.target as Node)) {
    protocolDropdownOpen.value = false;
  }

  if (!typeWrapperRef.value?.contains(event.target as Node)) {
    typeDropdownOpen.value = false;
  }
};

onMounted(async () => {
  document.addEventListener('mousedown', handleProtocolClickOutside);
  await store.fetchSupportedTypes();
  await store.fetchClients();
});

onUnmounted(() => {
  document.removeEventListener('mousedown', handleProtocolClickOutside);
});

const getTypeName = (type: string) => {
  const t = store.supportedTypes.find(t => t.type === type);
  return t ? t.name : type;
};

const getTypeNameShort = (type: string) => {
  if (type === 'qbittorrent') return 'QB';
  if (type === 'transmission') return 'TR';
  return getTypeName(type);
};

const getTypeBadgeClass = (type: string) => {
  if (type === 'qbittorrent') return 'badge-qb';
  if (type === 'transmission') return 'badge-tr';
  return 'bg-secondary';
};

const openAddModal = () => {
  isEdit.value = false;
  portTouched.value = false;
  Object.assign(form, {
    id: '',
    name: '',
    type: '',
    host: 'localhost',
    port: 8080,
    username: '',
    password: '',
    apikey: '',
    enabled: true,
    enable: true,
  });
  syncHostInputValue();
  showModal.value = true;
};

const openEditModal = (client: TorrentClient) => {
  isEdit.value = true;
  portTouched.value = false;
  Object.assign(form, client);
  // 密码掩码显示，真实密码保留用于后续操作
  const hasPassword = Boolean((client as any).password);
  const hasApiKey = Boolean((client as any).apikey);
  originalPassword.value = (client as any).password || '';
  originalApiKey.value = (client as any).apikey || '';
  form.password = hasPassword ? '*'.repeat(originalPassword.value.length) : '';
  form.apikey = hasApiKey ? '*'.repeat(originalApiKey.value.length) : '';
  normalizeHostInput(form.host || '');
  syncHostInputValue();
  showModal.value = true;
};

const onTypeChange = () => {
  const t = store.supportedTypes.find(t => t.type === form.type);
  if (!t) {
    return;
  }

  if (!portTouched.value || !form.port) {
    form.port = t.default_port;
  }
};


const handleSaveClient = async () => {
  if (!form.name || !form.type || !form.host || !form.port) {
    toast.error('请填写必填项');
    return;
  }
  
  saving.value = true;
  try {
    const payload: Downloader = {
      id: form.id,
      name: form.name,
      type: form.type,
      host: form.host,
      port: form.port,
      username: form.username,
      password: form.password,
      apikey: form.apikey,
      enabled: form.enabled,
      enable: form.enable,
      version: form.version,
    };
    // 保存前先测试连接并带上版本号，一次保存完成
    // 测试时使用真实密码（如果用户未修改密码，则用原始密码）
    const testPayload: Downloader = { ...payload };
    if (originalPassword.value && testPayload.password === '*'.repeat(originalPassword.value.length)) {
      testPayload.password = originalPassword.value;
    }
    if (originalApiKey.value && testPayload.apikey === '*'.repeat(originalApiKey.value.length)) {
      testPayload.apikey = originalApiKey.value;
    }
    try {
      const testRes = await store.testConnectionConfig(testPayload);
      if (testRes.success && testRes.version) {
        payload.version = testRes.version;
      }
    } catch (e) {
      console.warn('保存前测试连接获取版本失败', e);
    }

    // 保存时只发送实际新密码，避免用 ******** 覆盖已有密码
    if ((originalPassword.value && payload.password === '*'.repeat(originalPassword.value.length)) || payload.password === '') {
      delete payload.password;
    }
    if ((originalApiKey.value && payload.apikey === '*'.repeat(originalApiKey.value.length)) || payload.apikey === '') {
      delete payload.apikey;
    }

    if (isEdit.value) {
      await store.updateClient(form.id, payload);
    } else {
      await store.addClient(payload);
    }

    showModal.value = false;
    originalPassword.value = '';
    originalApiKey.value = '';
    toast.success('保存成功');
  } catch (e) {
    toast.error('保存失败');
  } finally {
    saving.value = false;
  }
};

const confirmDelete = async (client: TorrentClient) => {
  if (await confirm(`确定要删除 ${client.name} 吗？`, '删除确认')) {
    try {
      await store.deleteClient(client.id);
      toast.success('删除成功');
    } catch (e) {
      toast.error('删除失败');
    }
  }
};

const testConnection = async (id: string) => {
  testing.value = id;
  try {
    const res = await store.testConnection(id);
    if (res.success) {
      toast.success(res.message);
      if (res.version) {
        const client = store.clients.find(c => c.id === id);
        if (client) {
          client.version = res.version;
        }
      }
    } else {
      toast.error(res.message);
    }
  } catch (e) {
    toast.error('测试失败');
  } finally {
    testing.value = null;
  }
};

const testConfig = async () => {
  testingConfig.value = true;
  try {
    // 测试时使用真实密码（如果用户未修改密码，则用原始密码）
    const testPayload = { ...form };
    if (originalPassword.value && testPayload.password === '*'.repeat(originalPassword.value.length)) {
      testPayload.password = originalPassword.value;
    }
    if (originalApiKey.value && testPayload.apikey === '*'.repeat(originalApiKey.value.length)) {
      testPayload.apikey = originalApiKey.value;
    }
    const res = await store.testConnectionConfig(testPayload);
    if (res.success) {
      toast.success(res.message);
    } else {
      toast.error(res.message);
    }
  } catch (e) {
    toast.error('测试失败');
  } finally {
    testingConfig.value = false;
  }
};

const importResultBadgeText = computed(() => {
  if (!lastImportResult.value) return '';
  if (lastImportResult.value.imported > 0) return '已导入';
  if (lastImportResult.value.cloudflare_domains.length > 0) return '无新增';
  return '仅扫描';
});

const visibleCloudflareDomains = computed(() => {
  const domains = lastImportResult.value?.cloudflare_domains || [];
  return showAllCloudflareDomains.value ? domains : domains.slice(0, IMPORT_RESULT_PREVIEW_LIMIT);
});

const visibleNonCloudflareDomains = computed(() => {
  const domains = lastImportResult.value?.non_cloudflare_domains || [];
  return showAllNonCloudflareDomains.value ? domains : domains.slice(0, IMPORT_RESULT_PREVIEW_LIMIT);
});

const importClientSummaryItems = computed(() => {
  const summary = lastImportResult.value?.client_summary || '';
  return summary
    .split('；')
    .map(item => item.trim())
    .filter(Boolean);
});

const handleImportTrackers = async () => {
  importing.value = true;
  try {
    const res = await store.importTrackers();
    toast.info(res.message || '后台任务已启动');
  } catch (e: any) {
    toast.error('导入失败: ' + getErrorMessage(e, '未知错误'));
  } finally {
    importing.value = false;
  }
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

.clients-layout {
  display: flex;
  flex: 1 1 auto;
  min-height: 0;
  min-width: 0;
}

.workspace-card {
  min-width: 0;
  border-radius: 1.4rem;
  background: var(--bg-surface);
  border: 1px solid rgba(161, 172, 184, 0.14);
  box-shadow: var(--shadow-sm);
}

.clients-card {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  min-height: 0;
  min-width: 0;
  padding: 1.5rem;
  overflow: hidden;
}

.clients-content {
  flex: 1 1 auto;
  min-height: 0;
  min-width: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding-top: 0.35rem;
  padding-right: 0.2rem;
}

.workspace-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.clients-card-header {
  align-items: center;
}

.clients-card-heading {
  flex: 1 1 240px;
}

.clients-card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.85rem;
}

.workspace-card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-heading);
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

.action-btn:focus-visible {
  outline: none;
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

.action-btn-success {
  background: rgba(74, 179, 126, 0.12);
  color: var(--success-color);
  border-color: rgba(74, 179, 126, 0.18);
}

.action-btn-success:hover:not(:disabled),
.action-btn-success:focus-visible:not(:disabled) {
  background: rgba(74, 179, 126, 0.16);
  border-color: rgba(74, 179, 126, 0.28);
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

.clients-loading .spinner-border {
  width: 2rem;
  height: 2rem;
}

.import-result-panel {
  margin-bottom: 1.2rem;
  padding: 1.1rem;
  border-radius: 1.15rem;
  border: 1px solid rgba(var(--primary-rgb), 0.12);
  background: linear-gradient(180deg, rgba(var(--primary-rgb), 0.06), transparent 100%), var(--bg-surface-alt);
  box-shadow: var(--shadow-sm);
}

.import-result-panel.is-success {
  border-color: rgba(74, 179, 126, 0.2);
  background: linear-gradient(180deg, rgba(74, 179, 126, 0.08), transparent 100%), var(--bg-surface-alt);
}

.import-result-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.import-result-title-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.import-result-title-row h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-heading);
}

.import-result-head p {
  margin: 0.38rem 0 0;
  color: var(--text-muted);
  line-height: 1.6;
}

.import-result-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 1.75rem;
  padding: 0.2rem 0.62rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
}

.import-result-badge.success {
  color: var(--success-color);
  background: rgba(74, 179, 126, 0.14);
}

.import-result-badge.neutral {
  color: var(--primary-color);
  background: rgba(var(--primary-rgb), 0.1);
}

.import-result-dismiss {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: 0;
  border-radius: 0.72rem;
  background: transparent;
  color: var(--text-muted);
  transition: background-color var(--transition-fast), color var(--transition-fast), transform var(--transition-fast);
}

.import-result-dismiss:hover,
.import-result-dismiss:focus-visible {
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
  transform: translateY(-1px);
  outline: none;
}

.import-result-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.85rem;
  margin-bottom: 0.95rem;
}

.import-result-stat-card {
  display: grid;
  gap: 0.28rem;
  padding: 0.9rem 0.95rem;
  border-radius: 0.95rem;
  border: 1px solid var(--divider-color);
  background: color-mix(in srgb, var(--bg-surface) 88%, transparent);
}

.import-result-stat-card span,
.import-result-block-head p {
  color: var(--text-muted);
  font-size: 0.76rem;
}

.import-result-stat-card strong {
  color: var(--text-heading);
  font-size: 1.38rem;
  line-height: 1.1;
}

.import-result-stat-card small {
  color: var(--text-muted);
  line-height: 1.45;
}

.import-result-stat-highlight {
  border-color: rgba(74, 179, 126, 0.2);
  background: linear-gradient(180deg, rgba(74, 179, 126, 0.08), transparent 100%), color-mix(in srgb, var(--bg-surface) 88%, transparent);
}

.import-result-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
  margin-bottom: 0.9rem;
}

.import-result-block {
  padding: 0.95rem;
  border-radius: 1rem;
  border: 1px solid var(--divider-color);
  background: color-mix(in srgb, var(--bg-surface) 92%, transparent);
}

.import-result-block-success {
  border-color: rgba(74, 179, 126, 0.2);
}

.import-result-block-muted {
  border-color: rgba(161, 172, 184, 0.18);
}

.import-result-block-summary {
  border-color: rgba(var(--primary-rgb), 0.14);
}

.import-result-block-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.8rem;
  margin-bottom: 0.8rem;
}

.import-result-block-head h5 {
  margin: 0;
  color: var(--text-heading);
  font-size: 0.92rem;
  font-weight: 700;
}

.import-result-block-head p {
  margin: 0.24rem 0 0;
  line-height: 1.5;
}

.import-result-count {
  flex: 0 0 auto;
  min-width: 2rem;
  height: 2rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 0.55rem;
  border-radius: 999px;
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
  font-size: 0.8rem;
  font-weight: 700;
}

.import-result-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}

.import-result-chip {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  padding: 0.34rem 0.62rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--bg-surface-alt) 85%, transparent);
  border: 1px solid var(--divider-color);
  color: var(--text-heading);
  font-size: 0.78rem;
  line-height: 1.4;
  word-break: break-all;
}

.import-result-chip-success {
  border-color: rgba(74, 179, 126, 0.18);
  background: rgba(74, 179, 126, 0.1);
  color: color-mix(in srgb, var(--success-color) 88%, var(--text-heading));
}

.import-result-empty {
  color: var(--text-muted);
  font-size: 0.84rem;
  line-height: 1.55;
}

.import-result-link {
  margin-top: 0.72rem;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--primary-color);
  font-size: 0.82rem;
  font-weight: 600;
}

.import-result-link:hover,
.import-result-link:focus-visible {
  text-decoration: underline;
  outline: none;
}

.import-result-summary-list {
  display: grid;
  gap: 0.6rem;
}

.import-result-summary-item {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  padding: 0.72rem 0.78rem;
  border-radius: 0.88rem;
  background: color-mix(in srgb, var(--bg-surface-alt) 90%, transparent);
  border: 1px solid var(--divider-color);
  color: var(--text-heading);
  line-height: 1.55;
}

.import-result-summary-item i {
  margin-top: 0.08rem;
  color: var(--primary-color);
}

.client-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;
  align-content: start;
}

.client-card {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  padding: 1.25rem;
  border-radius: 1.15rem;
  border: 1px solid var(--border-color);
  background: linear-gradient(180deg, color-mix(in srgb, var(--bg-surface) 88%, transparent) 0%, color-mix(in srgb, var(--bg-surface-alt) 96%, transparent) 100%);
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-base), box-shadow var(--transition-base), border-color var(--transition-base);
  overflow: hidden;
}

.client-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  border-color: rgba(var(--primary-rgb), 0.18);
}

.client-card-top {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  margin-bottom: 1rem;
}

.client-title-block {
  min-width: 0;
}

.client-title-line {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.9rem;
}

.client-title-block h4 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-heading);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.client-title-block p {
  margin: 0.45rem 0 0;
  color: var(--text-muted);
  font-size: 0.9rem;
  word-break: break-word;
}

.client-badges {
  display: flex;
  flex-wrap: nowrap;
  justify-content: flex-end;
  align-items: center;
  gap: 0.45rem;
  white-space: nowrap;
}

.client-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 1.58rem;
  padding: 0.22rem 0.48rem;
  border-radius: 0.78rem;
  font-size: 0.68rem;
  line-height: 1;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.client-version {
  text-transform: none;
}

.client-meta-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
  margin-bottom: 1rem;
}

.client-meta-item {
  display: flex;
  flex-direction: column;
  gap: 0.32rem;
  padding: 0.72rem 0.9rem;
  border-radius: 0.95rem;
  background: color-mix(in srgb, var(--bg-surface-alt) 88%, transparent);
  border: 1px solid var(--divider-color);
  min-width: 0;
}

.client-meta-item span {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.client-meta-item strong {
  color: var(--text-heading);
  font-size: 0.88rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.client-meta-full {
  grid-column: 1 / -1;
}

.client-card-actions {
  display: flex;
  gap: 0.65rem;
  margin-top: auto;
}

.client-action-btn {
  flex: 1 1 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  border-radius: 0.9rem;
  min-height: 2.45rem;
  padding: 0.56rem 0.78rem;
  font-size: 0.86rem;
  font-weight: 600;
  transition: transform var(--transition-base), box-shadow var(--transition-base), border-color var(--transition-base), background-color var(--transition-base);
}

.client-action-btn span {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  white-space: nowrap;
}

.client-action-btn:hover:not(:disabled),
.client-action-btn:focus-visible:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.client-action-btn:focus-visible {
  outline: none;
}

.client-action-btn:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.client-action-primary {
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
  border-color: rgba(var(--primary-rgb), 0.16);
}

.client-action-success {
  background: rgba(74, 179, 126, 0.12);
  color: var(--success-color);
  border-color: rgba(74, 179, 126, 0.18);
}

.client-action-danger {
  background: rgba(225, 108, 108, 0.1);
  color: var(--danger-color);
  border-color: rgba(225, 108, 108, 0.16);
}

.client-modal {
  background: var(--bg-overlay);
}

.client-modal-dialog {
  max-width: 45rem;
  padding: 0.85rem;
}

.client-modal-content {
  border: 1px solid rgba(161, 172, 184, 0.16);
  border-radius: 1.2rem;
  overflow: hidden;
  background: color-mix(in srgb, var(--bg-surface) 94%, white 6%);
  box-shadow: 0 1.1rem 2.4rem rgba(15, 23, 42, 0.16);
}

.client-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 1rem 1.15rem 0.85rem;
  border-bottom: 1px solid var(--divider-color);
  background: linear-gradient(180deg, rgba(var(--primary-rgb), 0.055), transparent 100%);
}

.client-modal-title-wrap {
  min-width: 0;
}

.client-modal-header .modal-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-heading);
}

.client-modal-header p {
  margin: 0.24rem 0 0;
  color: var(--text-muted);
  font-size: 0.84rem;
  line-height: 1.45;
}

.client-modal-close {
  flex-shrink: 0;
  margin: 0;
}

.client-modal-body {
  padding: 1rem 1.15rem;
}

.client-modal-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.client-form-panel {
  padding: 0.9rem;
  border: 1px solid rgba(161, 172, 184, 0.14);
  border-radius: 0.95rem;
  background: color-mix(in srgb, var(--bg-surface-alt) 72%, transparent);
}

.client-form-panel-main {
  background: linear-gradient(180deg, rgba(var(--primary-rgb), 0.04), transparent 100%);
}

.client-form-panel-head {
  margin-bottom: 0.75rem;
}

.client-form-panel-head-inline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.client-form-panel-head h6 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-heading);
}

.client-form-panel-head span {
  display: block;
  margin-top: 0.3rem;
  color: var(--text-muted);
  font-size: 0.81rem;
}

.client-form-label {
  margin-bottom: 0.48rem;
  color: var(--text-heading);
  font-size: 0.88rem;
  font-weight: 600;
}

.client-input-group:not(.client-host-group) {
  display: flex;
  align-items: stretch;
  border-radius: 0.9rem;
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: var(--border-color);
}

.client-input-group > :deep(.input-group-text) {
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

.client-input-group > :deep(.form-control),
.client-input-group > :deep(.form-select) {
  position: relative;
  flex: 1 1 auto;
  width: 1%;
  min-height: 2.9rem;
  border: 0;
  background: var(--bg-surface) !important;
  background-color: var(--bg-surface) !important;
  background-clip: border-box;
  color: color-mix(in srgb, var(--text-heading) 78%, var(--text-muted));
  -webkit-text-fill-color: color-mix(in srgb, var(--text-heading) 78%, var(--text-muted));
  box-shadow: none;
  border-top-left-radius: 0 !important;
  border-bottom-left-radius: 0 !important;
  border-top-right-radius: 0.9rem !important;
  border-bottom-right-radius: 0.9rem !important;
}

.client-input-group > :deep(.form-select) {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-image: none !important;
}

.client-input-group > :deep(.form-control::placeholder) {
  color: color-mix(in srgb, var(--text-muted) 88%, transparent);
}

.client-input-group > :deep(.form-control:focus),
.client-input-group > :deep(.form-select:focus) {
  z-index: 3;
  margin-left: 0;
  box-shadow: inset 0 0 0 1px rgba(var(--primary-rgb), 0.34), 0 0 0 0.2rem rgba(var(--primary-rgb), 0.12);
}

.client-host-wrapper {
  width: 100%;
}

.client-type-wrapper {
  width: 100%;
}

.client-type-group.is-disabled {
  opacity: 0.78;
}

.client-type-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.68rem 0.92rem;
  text-align: left;
  cursor: pointer;
}

.client-type-trigger span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.client-type-trigger span.is-placeholder {
  color: color-mix(in srgb, var(--text-muted) 88%, transparent);
}

.client-type-trigger i {
  flex: 0 0 auto;
  font-size: 1rem;
  color: var(--text-muted);
  transition: transform 0.2s ease, color 0.2s ease;
}

.client-type-trigger i.is-open {
  transform: rotate(180deg);
  color: var(--primary-color);
}

.client-type-trigger:disabled {
  cursor: not-allowed;
}

.client-host-group {
  position: relative;
  display: flex;
  align-items: stretch;
  border-radius: 0.9rem;
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: var(--border-color);
}

.client-host-group > :deep(.input-group-text) {
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

.client-protocol-trigger {
  position: absolute;
  top: 50%;
  right: 0.35rem;
  transform: translateY(-50%);
  display: none;
  align-items: center;
  justify-content: center;
  gap: 0.18rem;
  min-width: 1.75rem;
  height: 1.75rem;
  padding: 0;
  border: 0;
  border-radius: 0.55rem;
  background: transparent;
  color: var(--text-muted);
  transition: background-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
  z-index: 2;
}

.client-protocol-trigger span {
  display: none;
}

.client-protocol-trigger i {
  font-size: 1rem;
  transition: transform 0.2s ease;
}

.client-protocol-trigger.is-open i {
  transform: rotate(180deg);
}

.client-protocol-trigger:hover,
.client-protocol-trigger.is-open {
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
}

.client-host-group :deep(.client-host-input) {
  border-top-left-radius: 0 !important;
  border-bottom-left-radius: 0 !important;
  border-top-right-radius: 0.9rem !important;
  border-bottom-right-radius: 0.9rem !important;
  padding-right: 2.75rem;
}

.client-host-clear-btn {
  position: absolute;
  top: 50%;
  right: 0.55rem;
  transform: translateY(-50%);
  width: 1.55rem;
  height: 1.55rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 50% !important;
  background: transparent !important;
  background-clip: padding-box;
  color: var(--text-muted);
  appearance: none;
  -webkit-appearance: none;
  transition: background-color 0.2s ease, color 0.2s ease;
  outline: none;
  box-shadow: none;
  z-index: 2;
}

.client-host-clear-btn i {
  font-size: 0.88rem;
}

.client-host-clear-btn:hover,
.client-host-clear-btn:focus-visible {
  background: rgba(var(--primary-rgb), 0.16) !important;
  color: var(--primary-color);
  outline: none;
  box-shadow: none;
}

.client-protocol-dropdown {
  position: absolute;
  top: calc(100% + 0.55rem);
  left: 50%;
  transform: translateX(-50%);
  width: min(13rem, 100%);
  z-index: 30;
  isolation: isolate;
  padding: 0.45rem;
  display: grid;
  gap: 0.36rem;
  border-radius: 0.95rem;
  border: 1px solid rgba(var(--primary-rgb), 0.1);
  background: color-mix(in srgb, var(--bg-surface) 92%, white 8%);
  backdrop-filter: blur(14px) saturate(145%);
  -webkit-backdrop-filter: blur(14px) saturate(145%);
  box-shadow: 0 0.85rem 1.7rem rgba(15, 23, 42, 0.1);
}

.client-protocol-dropdown::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  border-radius: inherit;
  background: var(--bg-surface);
}

.client-type-dropdown {
  position: absolute;
  top: calc(100% + 0.55rem);
  left: 0;
  right: 0;
  z-index: 30;
  isolation: isolate;
  padding: 0.45rem;
  display: grid;
  gap: 0.36rem;
  border-radius: 0.95rem;
  border: 1px solid rgba(var(--primary-rgb), 0.1);
  background: color-mix(in srgb, var(--bg-surface) 92%, white 8%);
  backdrop-filter: blur(14px) saturate(145%);
  -webkit-backdrop-filter: blur(14px) saturate(145%);
  box-shadow: 0 0.85rem 1.7rem rgba(15, 23, 42, 0.1);
}

.client-type-dropdown::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  border-radius: inherit;
  background: var(--bg-surface);
}

.client-type-dropdown-note {
  padding-bottom: 0.2rem;
}

.client-type-option span {
  text-transform: uppercase;
}

.client-protocol-dropdown-note {
  display: grid;
  gap: 0.18rem;
  padding: 0.2rem 0.32rem 0.12rem;
}

.client-protocol-dropdown-note strong {
  font-size: 0.79rem;
  color: var(--text-heading);
}

.client-protocol-dropdown-note span {
  font-size: 0.74rem;
  line-height: 1.45;
  color: var(--text-muted);
}

.client-protocol-option {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
  gap: 0.8rem;
  padding: 0.56rem 0.68rem;
  border: 1px solid transparent;
  border-radius: 0.8rem;
  background: transparent;
  text-align: left;
  transition: background-color var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.client-protocol-option strong {
  font-size: 0.84rem;
  color: var(--text-heading);
}

.client-protocol-option span {
  font-size: 0.76rem;
  color: var(--text-muted);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

.client-protocol-option:hover,
.client-protocol-option.is-active {
  background: rgba(var(--primary-rgb), 0.08);
  border-color: rgba(var(--primary-rgb), 0.12);
  box-shadow: none;
}

.client-switch-stack {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.6rem;
}

.client-switch-item {
  display: flex;
  align-items: center;
  gap: 0.72rem;
  min-height: 2.9rem;
  padding: 0.72rem 0.85rem;
  border: 1px solid rgba(161, 172, 184, 0.14);
  border-radius: 0.95rem;
  background: var(--bg-surface);
  margin: 0;
}

.client-switch-item-inline {
  min-height: auto;
  padding: 0;
  border: 0;
  background: transparent;
  justify-content: flex-end;
}

.client-switch-item .form-check-label {
  color: var(--text-heading);
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
}

.client-switch-item .form-check-input {
  width: 2.5rem;
  height: 1.35rem;
  margin: 0;
  cursor: pointer;
  float: none;
  flex-shrink: 0;
  background-color: rgba(161, 172, 184, 0.3);
  border-color: rgba(161, 172, 184, 0.3);
  box-shadow: none;
}

.client-switch-item .form-check-input:checked {
  background-color: rgba(var(--primary-rgb), 0.92);
  border-color: rgba(var(--primary-rgb), 0.92);
}

.client-switch-item .form-check-input:focus {
  box-shadow: 0 0 0 0.18rem rgba(var(--primary-rgb), 0.14);
  border-color: rgba(var(--primary-rgb), 0.42);
}

.client-modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 0.85rem 1.15rem 1rem;
  border-top: 1px solid var(--divider-color);
  background: color-mix(in srgb, var(--bg-surface-alt) 82%, transparent);
}

.client-modal-footer-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.client-modal-btn {
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

.client-modal-btn:hover:not(:disabled),
.client-modal-btn:focus-visible:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.client-modal-btn:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.client-modal-btn-primary {
  background: linear-gradient(135deg, rgba(var(--primary-rgb), 0.98), rgba(var(--primary-rgb), 0.82));
  color: #fff;
  box-shadow: 0 0.75rem 1.6rem rgba(var(--primary-rgb), 0.22);
}

.client-modal-btn-muted {
  background: color-mix(in srgb, var(--bg-surface-alt) 88%, transparent);
  border-color: rgba(161, 172, 184, 0.16);
  color: color-mix(in srgb, var(--text-heading) 74%, var(--text-muted));
}

.client-modal-btn-ghost {
  background: rgba(74, 179, 126, 0.12);
  border-color: rgba(74, 179, 126, 0.18);
  color: color-mix(in srgb, var(--success-color) 88%, var(--text-heading));
}

.badge-enabled {
  background: var(--bg-soft-success);
  color: var(--success-color);
}

.badge-disabled {
  background: color-mix(in srgb, var(--bg-surface-alt) 85%, var(--danger-color));
  color: #8b95a7;
}

.badge-qb {
  background: color-mix(in srgb, #60a5fa 18%, var(--bg-surface-alt));
  color: #4b83d6;
}

.badge-tr {
  background: color-mix(in srgb, #fb7185 18%, var(--bg-surface-alt));
  color: #e45b72;
}

.client-card {
  overflow: hidden;
}

.mono-text {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

@media (max-width: 1279.98px) {
  .client-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767.98px) {
  .clients-content {
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  .clients-content::-webkit-scrollbar {
    display: none;
    width: 0;
    height: 0;
  }

  .import-result-panel {
    padding: 0.95rem;
  }

  .import-result-head {
    flex-direction: column;
  }

  .import-result-dismiss {
    align-self: flex-end;
  }

  .import-result-stats,
  .import-result-grid {
    grid-template-columns: 1fr;
  }

  .client-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .clients-card {
    padding: 1rem;
  }

  .page-header-actions {
    width: 100%;
    order: 3;
  }

  .action-btn {
    flex: 1 1 0;
  }

  .workspace-pill {
    order: 2;
  }

  .clients-card-title-row {
    align-items: flex-start;
  }

  .client-card-top {
    gap: 0.55rem;
  }

  .client-badges {
    justify-content: flex-start;
  }

  .client-meta-list {
    grid-template-columns: 1fr;
  }

  .client-modal-dialog {
    padding: 0.6rem;
  }

  .client-modal-header,
  .client-modal-body,
  .client-modal-footer {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .client-form-panel-head-inline {
    align-items: center;
    flex-direction: row;
    justify-content: space-between;
  }

  .client-switch-item-inline {
    margin-left: auto;
    justify-content: flex-end;
  }

  .client-modal-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .client-modal-footer-actions {
    width: 100%;
  }

  .client-modal-btn,
  .client-modal-footer-actions .client-modal-btn {
    width: 100%;
  }

}
</style>
