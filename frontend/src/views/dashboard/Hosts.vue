<template>
  <div class="dashboard-redesign">
    <div class="page-header">
      <h2 class="page-title">Hosts源管理</h2>
      <Teleport to="#mobile-header-actions" :disabled="!isMobile">
        <div class="page-header-actions" v-if="isMobile || true">
        </div>
      </Teleport>
    </div>

    <section class="hosts-layout">
      <article class="workspace-card hosts-card">
        <header class="workspace-card-header hosts-card-header">
          <div class="hosts-card-heading">
            <div class="hosts-card-title-row">
              <h3>源列表</h3>
              <button class="action-btn action-btn-primary action-btn-compact" @click="showAddModal = true">
                <span>
                  <i class="bx bx-plus-circle"></i>
                  <span>添加源</span>
                </span>
              </button>
            </div>
            <p>集中管理 Hosts 订阅源启用状态、链接地址与基础信息。</p>
          </div>
        </header>

        <div class="hosts-content-area">
          <div v-if="store.loading" class="workspace-empty hosts-loading">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <span>正在加载 Hosts 源配置...</span>
          </div>

          <div v-else-if="store.sources.length === 0" class="workspace-empty hosts-empty">
            <i class="bx bx-data"></i>
            <strong>暂无 Hosts 源</strong>
            <span>点击右上角“添加源”开始配置 Hosts 源地址。</span>
          </div>

          <div v-else class="source-table">
            <div class="source-table-header">
              <div>名称</div>
              <div>源地址</div>
              <div>开关</div>
              <div>操作</div>
            </div>
            <div class="source-table-body">
              <div class="source-row" v-for="source in store.sources" :key="source.url">
                <div class="source-col-name">
                  <strong>{{ source.name }}</strong>
                </div>
                <div class="source-col-url mono-text" :title="source.url">{{ source.url }}</div>
                <div class="source-col-switch">
                  <label class="switch source-switch">
                    <input type="checkbox" :checked="source.enable" :disabled="isSourceToggling(source.url)" @change="toggleSource(source)">
                    <div class="slider">
                      <div class="circle">
                        <svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg">
                          <g>
                            <path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503-12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path>
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
                <div class="source-col-actions">
                  <button class="source-action-btn source-action-primary" @click="openEditModal(source)">
                    <span>
                      <i class="bx bx-pencil"></i>
                      <span>编辑</span>
                    </span>
                  </button>
                  <button class="source-action-btn source-action-danger" @click="confirmDelete(source)">
                    <span>
                      <i class="bx bx-trash"></i>
                      <span>删除</span>
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </article>

      <article class="workspace-card hosts-preview-card">
        <header class="workspace-card-header hosts-preview-header">
          <div class="hosts-card-heading">
            <div class="hosts-card-title-row">
              <h3>当前系统Hosts</h3>
              <button class="action-btn action-btn-warning action-btn-compact" @click="showEditModal = true">
                <span>
                  <i class="bx bx-pencil"></i>
                  <span>编辑Hosts</span>
                </span>
              </button>
            </div>
            <p>预览当前系统 Hosts 文件内容，必要时可进入编辑模式直接调整。</p>
          </div>
        </header>

        <div class="hosts-preview-body">
          <div class="hosts-preview-note">
            <i class="bx bx-info-circle"></i>
            <span>直接编辑系统 Hosts 前，请确认内容来源可信并已备份原文件。</span>
          </div>
          <div class="hosts-content-shell">
            <pre class="hosts-content">{{ store.currentHosts || '正在加载...' }}</pre>
          </div>
        </div>
      </article>
    </section>

    <!-- Add Modal -->
    <div v-if="showAddModal" class="modal fade show d-block hosts-source-modal" @click.self="showAddModal = false">
      <div class="modal-dialog modal-dialog-centered hosts-source-modal-dialog">
        <div class="modal-content hosts-source-modal-content">
          <div class="modal-header hosts-source-modal-header">
            <div class="hosts-source-modal-title-wrap">
              <h5 class="modal-title">{{ isEditing ? '编辑 Hosts 源' : '添加 Hosts 源' }}</h5>
              <p>填写基础信息后即可保存到 Hosts 源列表，支持随时启用或停用。</p>
            </div>
            <button type="button" class="btn-close hosts-source-modal-close" @click="showAddModal = false"></button>
          </div>
          <div class="modal-body hosts-source-modal-body">
            <form @submit.prevent="handleAddSource" class="hosts-source-modal-form">
              <section class="hosts-source-form-panel hosts-source-form-panel-main">
                <div class="hosts-source-form-panel-head hosts-source-form-panel-head-inline">
                  <div>
                    <h6>源配置</h6>
                  </div>
                  <div class="form-check form-switch hosts-source-switch-item hosts-source-switch-item-inline">
                    <input class="form-check-input" type="checkbox" id="hosts-source-enable" v-model="newSource.enable">
                    <label class="form-check-label" for="hosts-source-enable">启用</label>
                  </div>
                </div>

                <div class="row g-3">
                  <div class="col-12">
                    <label class="form-label hosts-source-form-label">源名称 <span class="text-danger">*</span></label>
                    <div class="input-group hosts-source-input-group">
                      <span class="input-group-text"><i class="bx bx-purchase-tag-alt"></i></span>
                      <input
                        type="text"
                        class="form-control"
                        v-model="newSource.name"
                        required
                        placeholder="如：常用加速 Hosts"
                      >
                    </div>
                  </div>
                  <div class="col-12">
                    <label class="form-label hosts-source-form-label">源地址 <span class="text-danger">*</span></label>
                    <div class="input-group hosts-source-input-group">
                      <span class="input-group-text"><i class="bx bx-link-alt"></i></span>
                      <input
                        type="url"
                        class="form-control"
                        v-model="newSource.url"
                        required
                        placeholder="https://example.com/hosts"
                      >
                    </div>
                  </div>
                </div>
              </section>
            </form>
          </div>
          <div class="modal-footer hosts-source-modal-footer">
            <div class="hosts-source-modal-footer-note">
              <i class="bx bx-info-circle"></i>
              <span>保存后可在列表中继续编辑、切换启用状态或删除。</span>
            </div>
            <div class="hosts-source-modal-footer-actions">
              <button type="button" class="hosts-source-modal-btn hosts-source-modal-btn-muted" @click="showAddModal = false">取消</button>
              <button type="submit" class="hosts-source-modal-btn hosts-source-modal-btn-primary" :disabled="adding" @click="handleAddSource">
                <span v-if="adding" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bx bx-save"></i>
                <span>{{ isEditing ? '保存配置' : '添加源配置' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Hosts Modal -->
    <div v-if="showEditModal" class="modal fade show d-block hosts-edit-modal" @click.self="showEditModal = false">
      <div class="modal-dialog modal-lg modal-dialog-centered hosts-edit-modal-dialog">
        <div class="modal-content hosts-edit-modal-content">
          <div class="modal-header hosts-edit-modal-header">
            <div class="hosts-edit-modal-title-wrap">
              <h5 class="modal-title">编辑 Hosts</h5>
              <p>可直接调整当前系统 Hosts 内容，保存后会立即写入目标文件。</p>
            </div>
            <button type="button" class="btn-close hosts-edit-modal-close" @click="showEditModal = false"></button>
          </div>
          <div class="modal-body hosts-edit-modal-body">
            <section class="hosts-edit-form-panel hosts-edit-form-panel-warning">
              <div class="hosts-edit-warning-note">
                <i class="bx bxs-error-alt"></i>
                <div>
                  <strong>谨慎修改</strong>
                  <span>此操作将直接修改系统 Hosts 文件，请确认内容正确后再保存。</span>
                </div>
              </div>
            </section>

            <section class="hosts-edit-form-panel hosts-edit-form-panel-editor">
              <div class="hosts-edit-form-panel-head">
                <h6>Hosts 内容</h6>
                <span>支持多行编辑，建议保留原有结构与注释格式。</span>
              </div>
              <div class="hosts-edit-textarea-shell">
                <textarea
                  class="form-control hosts-edit-textarea font-monospace"
                  rows="15"
                  v-model="editingContent"
                ></textarea>
              </div>
            </section>
          </div>
          <div class="modal-footer hosts-edit-modal-footer">
            <div class="hosts-edit-modal-footer-note">
              <i class="bx bx-shield-quarter"></i>
              <span>建议保存前先检查域名与 IP 映射格式，避免写入无效内容。</span>
            </div>
            <div class="hosts-edit-modal-footer-actions">
              <button type="button" class="hosts-edit-modal-btn hosts-edit-modal-btn-muted" @click="showEditModal = false">取消</button>
              <button type="button" class="hosts-edit-modal-btn hosts-edit-modal-btn-primary" @click="handleSaveHosts" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bx bx-save"></i>
                <span>保存 Hosts</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, watch } from 'vue';
import { useHostsStore, type HostsSource } from '../../stores/hosts';
import { useMobile } from '../../composables/useMobile';
import { useToast } from 'vue-toastification';
import { useConfirm } from '../../composables/useConfirm';

const store = useHostsStore();
const { isMobile } = useMobile();
const toast = useToast();
const { confirm } = useConfirm();

const showAddModal = ref(false);
const showEditModal = ref(false);
const adding = ref(false);
const isEditing = ref(false);
const editingSourceUrl = ref('');

const saving = ref(false);
const editingContent = ref('');
const togglingSourceUrls = ref<Set<string>>(new Set());

const newSource = reactive<HostsSource>({
  name: '',
  url: '',
  enable: true
});

onMounted(async () => {
  await store.fetchConfig();
  await store.fetchCurrentHosts();
});

watch(showEditModal, (val) => {
  if (val) {
    editingContent.value = store.currentHosts;
  }
});

const toggleSource = async (source: HostsSource) => {
  if (isSourceToggling(source.url)) return;
  const nextEnabled = !source.enable;
  togglingSourceUrls.value = new Set(togglingSourceUrls.value).add(source.url);
  try {
    await store.updateSource(source.url, { enable: nextEnabled });
    if (nextEnabled) {
      toast.success(`已启用源“${source.name}”`);
    } else {
      toast.success(`已关闭源“${source.name}”，后台正在重建 Hosts`);
    }
  } catch (e) {
    toast.error('更新失败');
    store.fetchConfig();
  } finally {
    const next = new Set(togglingSourceUrls.value);
    next.delete(source.url);
    togglingSourceUrls.value = next;
  }
};

const isSourceToggling = (url: string) => togglingSourceUrls.value.has(url);

const confirmDelete = async (source: HostsSource) => {
  if (await confirm(`确定要删除 ${source.name} 吗？`, '删除确认')) {
    try {
      await store.deleteSource(source.url);
      toast.success('删除成功');
    } catch (e) {
      toast.error('删除失败');
    }
  }
};

const handleAddSource = async () => {
  adding.value = true;
  try {
    if (isEditing.value) {
      // If URL changed, we might need to delete old and add new, or just update if backend supports it.
      // Assuming simple update for now, but if URL is key, we should probably delete old first if different.
      if (editingSourceUrl.value !== newSource.url) {
         await store.deleteSource(editingSourceUrl.value);
         await store.addSource({ ...newSource });
      } else {
         // Same URL, just update properties
         await store.updateSource(editingSourceUrl.value, { ...newSource });
      }
    } else {
      await store.addSource({ ...newSource });
    }
    showAddModal.value = false;
    resetForm();
    toast.success(isEditing.value ? '更新成功' : '添加成功');
  } catch (e) {
    toast.error(isEditing.value ? '更新失败' : '添加失败');
  } finally {
    adding.value = false;
  }
};

const openEditModal = (source: HostsSource) => {
  isEditing.value = true;
  editingSourceUrl.value = source.url;
  newSource.name = source.name;
  newSource.url = source.url;
  newSource.enable = source.enable;
  showAddModal.value = true;
};

const resetForm = () => {
  newSource.name = '';
  newSource.url = '';
  newSource.enable = true;
  isEditing.value = false;
  editingSourceUrl.value = '';
};

watch(showAddModal, (val) => {
  if (!val) {
    resetForm();
  }
});



const handleSaveHosts = async () => {
  if (!await confirm('确定要保存修改吗？', '保存确认')) return;
  saving.value = true;
  try {
    await store.saveHostsContent(editingContent.value);
    showEditModal.value = false;
    toast.success('保存成功');
  } catch (e) {
    toast.error('保存失败');
  } finally {
    saving.value = false;
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
  overflow: visible;
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
  gap: 0.75rem;
  flex-wrap: wrap;
}

.hosts-layout {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  flex: 1 1 auto;
  min-height: 0;
  overflow: visible;
}

.workspace-card {
  min-width: 0;
  border-radius: 1.4rem;
  background: var(--bg-surface);
  border: 1px solid rgba(161, 172, 184, 0.14);
  box-shadow: var(--shadow-sm);
}

.hosts-card,
.hosts-preview-card {
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  min-width: 0;
}

.hosts-preview-card {
  overflow: visible;
}

.hosts-content-area,
.hosts-preview-body {
  min-width: 0;
}

.hosts-preview-body {
  display: flex;
  flex-direction: column;
  min-height: 0;
  gap: 0.9rem;
}

.hosts-content-area {
  padding-top: 0.35rem;
}

.workspace-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.hosts-card-header,
.hosts-preview-header {
  align-items: center;
}

.hosts-card-heading {
  flex: 1 1 240px;
  min-width: 0;
}

.hosts-card-title-row {
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
  padding: 0.58rem 0.82rem;
  border-radius: 0.8rem;
  font-size: 0.84rem;
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

.action-btn-warning {
  background: rgba(255, 193, 7, 0.12);
  color: #b7791f;
  border-color: rgba(255, 193, 7, 0.18);
}

.action-btn-warning:hover:not(:disabled),
.action-btn-warning:focus-visible:not(:disabled) {
  background: rgba(255, 193, 7, 0.16);
  border-color: rgba(255, 193, 7, 0.28);
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

.hosts-loading .spinner-border {
  width: 2rem;
  height: 2rem;
}

.source-table {
  border: 1px solid rgba(161, 172, 184, 0.12);
  border-radius: 1rem;
  overflow: hidden;
  background: color-mix(in srgb, var(--bg-surface-alt) 72%, transparent);
}

.source-table-header,
.source-row {
  display: grid;
  grid-template-columns: 14.5rem minmax(0, 1fr) 4.5rem 9.6rem;
  column-gap: 1.15rem;
  align-items: center;
}

.source-table-header {
  padding: 0.62rem 0.9rem;
  border-bottom: 1px solid rgba(161, 172, 184, 0.12);
  color: var(--text-muted);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  background: color-mix(in srgb, var(--bg-surface) 86%, transparent);
}

.source-table-header > div {
  text-align: left;
}

.source-table-header > div:nth-child(3),
.source-table-header > div:nth-child(4) {
  text-align: center;
}

.source-table-body {
  display: flex;
  flex-direction: column;
}

.source-row {
  padding: 0.56rem 0.9rem;
  border-bottom: 1px solid rgba(161, 172, 184, 0.12);
  transition: background-color var(--transition-base);
}

.source-row:last-child {
  border-bottom: none;
}

.source-row:hover {
  background: rgba(161, 172, 184, 0.06);
}

.source-col-name,
.source-col-url,
.source-col-switch,
.source-col-actions {
  min-width: 0;
}

.source-col-switch {
  display: flex;
  align-items: center;
  justify-content: center;
}

.source-col-name strong {
  display: block;
  color: var(--text-heading);
  font-size: 0.86rem;
  font-weight: 700;
  white-space: nowrap;
}

.source-col-name {
  justify-self: start;
}

.source-col-url {
  min-width: 0;
  width: 100%;
  justify-self: start;
  padding-left: 0;
  text-align: left;
  color: var(--text-heading);
  font-size: 0.78rem;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.source-switch {
  flex-shrink: 0;
}

.source-col-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: center;
}

.source-action-btn {
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

.source-action-btn span {
  display: inline-flex;
  align-items: center;
  gap: 0.32rem;
}

.source-action-btn:hover:not(:disabled),
.source-action-btn:focus-visible:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.source-action-primary {
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
  border-color: rgba(var(--primary-rgb), 0.16);
}

.source-action-primary:hover:not(:disabled),
.source-action-primary:focus-visible:not(:disabled) {
  background: rgba(var(--primary-rgb), 0.14);
  border-color: rgba(var(--primary-rgb), 0.28);
}

.source-action-danger {
  background: rgba(225, 108, 108, 0.1);
  color: var(--danger-color);
  border-color: rgba(225, 108, 108, 0.16);
}

.source-action-danger:hover:not(:disabled),
.source-action-danger:focus-visible:not(:disabled) {
  background: rgba(225, 108, 108, 0.14);
  border-color: rgba(225, 108, 108, 0.28);
}

.hosts-preview-note {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.9rem 1rem;
  border-radius: 0.95rem;
  background: rgba(255, 193, 7, 0.08);
  border: 1px solid rgba(255, 193, 7, 0.16);
  color: #b7791f;
  min-width: 0;
}

.hosts-preview-note i {
  color: #b7791f;
  font-size: 1.05rem;
  flex: 0 0 auto;
  align-self: center;
}

.hosts-preview-note span {
  color: #b7791f;
  line-height: 1.55;
}

.hosts-content-shell {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  border-radius: 1rem;
  background: var(--bg-surface-alt);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.hosts-content {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  display: block;
  min-height: 24rem;
  max-height: 70vh;
  overflow: auto;
  padding: 1rem;
  margin: 0;
  border-radius: 0;
  background: transparent;
  border: none;
  color: var(--text-main);
  font-size: 0.8125rem;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
}

.hosts-source-modal {
  background: var(--bg-overlay);
}

.hosts-source-modal-dialog {
  max-width: 45rem;
  padding: 0.85rem;
}

.hosts-source-modal-content {
  border: 1px solid rgba(161, 172, 184, 0.16);
  border-radius: 1.2rem;
  overflow: hidden;
  background: color-mix(in srgb, var(--bg-surface) 94%, white 6%);
  box-shadow: 0 1.1rem 2.4rem rgba(15, 23, 42, 0.16);
}

.hosts-source-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 1rem 1.15rem 0.85rem;
  border-bottom: 1px solid var(--divider-color);
  background: color-mix(in srgb, transparent 28%, rgba(var(--primary-rgb), 0.06));
}

.hosts-source-modal-title-wrap {
  min-width: 0;
}

.hosts-source-modal-header .modal-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-heading);
}

.hosts-source-modal-header p {
  margin: 0.24rem 0 0;
  color: var(--text-muted);
  font-size: 0.84rem;
  line-height: 1.45;
}

.hosts-source-modal-close {
  flex-shrink: 0;
  margin: 0;
}

.hosts-source-modal-body {
  padding: 1rem 1.15rem;
}

.hosts-source-modal-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.hosts-source-form-panel {
  padding: 0.9rem;
  border: 1px solid rgba(161, 172, 184, 0.14);
  border-radius: 0.95rem;
  background: color-mix(in srgb, var(--bg-surface-alt) 58%, transparent);
}

.hosts-source-form-panel-main {
  background: linear-gradient(180deg, rgba(var(--primary-rgb), 0.04), transparent 100%);
}

.hosts-source-form-panel-head {
  margin-bottom: 0.75rem;
}

.hosts-source-form-panel-head-inline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.hosts-source-form-panel-head h6 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-heading);
}

.hosts-source-form-panel-head span {
  display: block;
  margin-top: 0.3rem;
  color: var(--text-muted);
  font-size: 0.81rem;
  line-height: 1.45;
}

.hosts-source-form-label {
  margin-bottom: 0.48rem;
  color: var(--text-heading);
  font-size: 0.88rem;
  font-weight: 600;
}

.hosts-source-input-group {
  display: flex;
  align-items: stretch;
  border-radius: 0.9rem;
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: var(--border-color);
}

.hosts-source-input-group :deep(.input-group-text) {
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

.hosts-source-input-group :deep(.form-control) {
  position: relative;
  flex: 1 1 auto;
  width: 1%;
  min-height: 2.9rem;
  border: 0;
  background: var(--bg-surface) !important;
  background-color: var(--bg-surface) !important;
  color: color-mix(in srgb, var(--text-heading) 78%, var(--text-muted));
  -webkit-text-fill-color: color-mix(in srgb, var(--text-heading) 78%, var(--text-muted));
  box-shadow: none;
  border-top-left-radius: 0 !important;
  border-bottom-left-radius: 0 !important;
  border-top-right-radius: 0.9rem !important;
  border-bottom-right-radius: 0.9rem !important;
}

.hosts-source-input-group :deep(.form-control::placeholder) {
  color: color-mix(in srgb, var(--text-muted) 88%, transparent);
}

.hosts-source-input-group :deep(.form-control:focus) {
  z-index: 3;
  margin-left: 0;
  box-shadow: inset 0 0 0 1px rgba(var(--primary-rgb), 0.34), 0 0 0 0.2rem rgba(var(--primary-rgb), 0.12);
}

.hosts-source-form-hint {
  margin: 0.48rem 0 0;
  color: var(--text-muted);
  font-size: 0.78rem;
  line-height: 1.5;
}

.hosts-source-switch-item {
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

.hosts-source-switch-item-inline {
  min-height: auto;
  padding: 0;
  border: 0;
  background: transparent;
  justify-content: flex-end;
}

.hosts-source-switch-item .form-check-label {
  color: var(--text-heading);
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
}

.hosts-source-switch-item .form-check-input {
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

.hosts-source-switch-item .form-check-input:checked {
  background-color: rgba(var(--primary-rgb), 0.92);
  border-color: rgba(var(--primary-rgb), 0.92);
}

.hosts-source-switch-item .form-check-input:focus {
  box-shadow: 0 0 0 0.18rem rgba(var(--primary-rgb), 0.14);
  border-color: rgba(var(--primary-rgb), 0.42);
}

.hosts-source-modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 0.85rem 1.15rem 1rem;
  border-top: 1px solid var(--divider-color);
  background: color-mix(in srgb, var(--bg-surface-alt) 82%, transparent);
}

.hosts-source-modal-footer-note {
  display: inline-flex;
  align-items: center;
  gap: 0.42rem;
  min-width: 0;
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.45;
}

.hosts-source-modal-footer-note i {
  color: var(--primary-color);
  font-size: 0.95rem;
  flex-shrink: 0;
}

.hosts-source-modal-footer-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.hosts-source-modal-btn {
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

.hosts-source-modal-btn:hover:not(:disabled),
.hosts-source-modal-btn:focus-visible:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.hosts-source-modal-btn:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.hosts-source-modal-btn-primary {
  background: color-mix(in srgb, rgba(var(--primary-rgb), 0.98) 100%, rgba(var(--primary-rgb), 0.82));
  color: #fff;
  box-shadow: 0 0.75rem 1.6rem rgba(var(--primary-rgb), 0.22);
}

.hosts-source-modal-btn-muted {
  background: color-mix(in srgb, var(--bg-surface-alt) 88%, transparent);
  border-color: rgba(161, 172, 184, 0.16);
  color: color-mix(in srgb, var(--text-heading) 74%, var(--text-muted));
}

.hosts-edit-modal {
  background: var(--bg-overlay);
}

.hosts-edit-modal-dialog {
  max-width: 45rem;
  padding: 0.85rem;
}

.hosts-edit-modal-content {
  border: 1px solid rgba(161, 172, 184, 0.16);
  border-radius: 1.2rem;
  overflow: hidden;
  background: color-mix(in srgb, var(--bg-surface) 94%, white 6%);
  box-shadow: 0 1.1rem 2.4rem rgba(15, 23, 42, 0.16);
}

.hosts-edit-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 1rem 1.15rem 0.85rem;
  border-bottom: 1px solid var(--divider-color);
  background: color-mix(in srgb, transparent 28%, rgba(var(--primary-rgb), 0.06));
}

.hosts-edit-modal-title-wrap {
  min-width: 0;
}

.hosts-edit-modal-header .modal-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-heading);
}

.hosts-edit-modal-header p {
  margin: 0.24rem 0 0;
  color: var(--text-muted);
  font-size: 0.84rem;
  line-height: 1.45;
}

.hosts-edit-modal-close {
  flex-shrink: 0;
  margin: 0;
}

.hosts-edit-modal-body {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  padding: 0.9rem 1.05rem;
}

.hosts-edit-form-panel {
  padding: 0.78rem 0.82rem;
  border: 1px solid rgba(161, 172, 184, 0.14);
  border-radius: 0.95rem;
  background: color-mix(in srgb, var(--bg-surface-alt) 58%, transparent);
}

.hosts-edit-form-panel-warning {
  border-color: rgba(255, 193, 7, 0.34);
  background: color-mix(in srgb, rgba(255, 193, 7, 0.18) 100%, var(--bg-surface));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.16);
}

.hosts-edit-form-panel-editor {
  background: color-mix(in srgb, var(--bg-surface-alt) 54%, rgba(var(--primary-rgb), 0.04));
}

.hosts-edit-warning-note {
  display: flex;
  align-items: center;
  gap: 0.62rem;
}

.hosts-edit-warning-note > div {
  color: #b56a00;
}

.hosts-edit-warning-note i {
  color: #b56a00;
  font-size: 1.1rem;
  flex-shrink: 0;
  margin-top: 0;
  filter: drop-shadow(0 0 0.35rem rgba(181, 106, 0, 0.2));
}

.hosts-edit-warning-note strong {
  display: block;
  margin-bottom: 0.18rem;
  color: #b56a00;
  font-size: 0.88rem;
  font-weight: 700;
}

.hosts-edit-warning-note span {
  color: #b56a00;
  font-size: 0.8rem;
  line-height: 1.5;
}

.hosts-edit-form-panel-head {
  margin-bottom: 0.62rem;
}

.hosts-edit-form-panel-head h6 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-heading);
}

.hosts-edit-form-panel-head span {
  display: block;
  margin-top: 0.2rem;
  color: var(--text-muted);
  font-size: 0.81rem;
  line-height: 1.45;
}

.hosts-edit-textarea-shell {
  border: 1px solid var(--border-color);
  border-radius: 0.95rem;
  overflow: hidden;
  background: var(--bg-surface);
}

.hosts-edit-textarea {
  min-height: 21.5rem;
  resize: vertical;
  border: 0;
  border-radius: 0.95rem !important;
  background: transparent !important;
  color: var(--text-main);
  font-size: 0.83rem;
  line-height: 1.65;
  box-shadow: none !important;
}

.hosts-edit-textarea:focus {
  box-shadow: inset 0 0 0 1px rgba(var(--primary-rgb), 0.34), 0 0 0 0.2rem rgba(var(--primary-rgb), 0.12) !important;
}

.hosts-edit-modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 0.85rem 1.15rem 1rem;
  border-top: 1px solid var(--divider-color);
  background: color-mix(in srgb, var(--bg-surface-alt) 82%, transparent);
}

.hosts-edit-modal-footer-note {
  display: inline-flex;
  align-items: center;
  gap: 0.42rem;
  min-width: 0;
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.45;
}

.hosts-edit-modal-footer-note i {
  color: var(--primary-color);
  font-size: 0.95rem;
  flex-shrink: 0;
}

.hosts-edit-modal-footer-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.hosts-edit-modal-btn {
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

.hosts-edit-modal-btn:hover:not(:disabled),
.hosts-edit-modal-btn:focus-visible:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.hosts-edit-modal-btn:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.hosts-edit-modal-btn-primary {
  background: color-mix(in srgb, rgba(var(--primary-rgb), 0.98) 100%, rgba(var(--primary-rgb), 0.82));
  color: #fff;
  box-shadow: 0 0.75rem 1.6rem rgba(var(--primary-rgb), 0.22);
}

.hosts-edit-modal-btn-muted {
  background: color-mix(in srgb, var(--bg-surface-alt) 88%, transparent);
  border-color: rgba(161, 172, 184, 0.16);
  color: color-mix(in srgb, var(--text-heading) 74%, var(--text-muted));
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

@media (max-width: 767.98px) {
  .hosts-card,
  .hosts-preview-card {
    padding: 1rem;
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

  .hosts-card-title-row .action-btn {
    flex: 0 0 auto;
    width: auto;
  }

  .hosts-card-title-row,
  .source-col-switch,
  .source-col-actions {
    gap: 0.7rem;
  }

  .source-table {
    border-radius: 1rem;
    border-left: 1px solid rgba(161, 172, 184, 0.12);
    border-right: 1px solid rgba(161, 172, 184, 0.12);
  }

  .source-table-header {
    display: none;
  }

  .source-row {
    grid-template-columns: minmax(0, 1fr) auto;
    grid-template-areas:
      "name toggle"
      "url url"
      "actions actions";
    align-items: center;
    gap: 0.8rem;
    padding: 1rem 0.2rem;
  }

  .source-col-name {
    grid-area: name;
    align-self: center;
  }

  .source-col-switch {
    grid-area: toggle;
    justify-self: end;
  }

  .source-col-url {
    grid-area: url;
    width: 100%;
  }

  .source-col-actions {
    grid-area: actions;
    width: 100%;
    justify-content: flex-end;
  }

  .source-action-btn {
    flex: 0 0 auto;
  }

  .hosts-source-modal-dialog {
    padding: 0.6rem;
  }

  .hosts-source-modal-header,
  .hosts-source-modal-body,
  .hosts-source-modal-footer {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .hosts-source-form-panel-head-inline {
    align-items: center;
    flex-direction: row;
    justify-content: space-between;
  }

  .hosts-source-switch-item-inline {
    margin-left: auto;
    justify-content: flex-end;
  }

  .hosts-source-modal-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .hosts-source-modal-footer-actions {
    width: 100%;
  }

  .hosts-source-modal-btn,
  .hosts-source-modal-footer-actions .hosts-source-modal-btn {
    width: 100%;
  }

  .hosts-edit-modal-dialog {
    padding: 0.6rem;
  }

  .hosts-edit-modal-header,
  .hosts-edit-modal-body,
  .hosts-edit-modal-footer {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .hosts-edit-warning-note {
    align-items: flex-start;
  }

  .hosts-edit-warning-note i {
    align-self: flex-start;
    margin-top: 0.08rem;
  }

  .hosts-edit-modal-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .hosts-edit-modal-footer-actions {
    width: 100%;
  }

  .hosts-edit-modal-btn,
  .hosts-edit-modal-footer-actions .hosts-edit-modal-btn {
    width: 100%;
  }
}
</style>
