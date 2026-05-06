<template>
  <div class="dashboard-redesign">
    <PageHeaderShell title="Hosts源管理" :is-mobile="isMobile" />

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
          <PageEmptyState
            v-if="store.loading"
            container-class="hosts-loading"
            loading
            description="正在加载 Hosts 源配置..."
          />

          <PageEmptyState
            v-else-if="store.sources.length === 0"
            container-class="hosts-empty"
            title="暂无 Hosts 源"
            description="点击右上角“添加源”开始配置 Hosts 源地址。"
          />

          <div v-else class="source-table">
            <div class="source-table-header">
              <div>名称</div>
              <div>源地址</div>
              <div>开关</div>
              <div>操作</div>
            </div>
            <div class="source-table-body">
              <div class="source-row" v-for="source in store.sources" :key="source.id || source.url">
                <div class="source-col-name">
                  <strong>{{ source.name }}</strong>
                </div>
                <div class="source-col-url mono-text" :title="source.url">{{ source.url }}</div>
                <div class="source-col-switch">
                  <label class="switch source-switch">
                    <input type="checkbox" :checked="source.enabled" :disabled="isSourceToggling(source.id || source.url)" @change="toggleSource(source)">
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
              <h3>{{ hostsPreviewTitle }}</h3>
              <button class="action-btn action-btn-warning action-btn-compact" @click="showEditModal = true">
                <span>
                  <i class="bx bx-pencil"></i>
                  <span>编辑 Hosts</span>
                </span>
              </button>
            </div>
            <p>{{ hostsPreviewDescription }}</p>
          </div>
        </header>

        <div class="hosts-preview-body">
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
                    <input class="form-check-input" type="checkbox" id="hosts-source-enable" v-model="newSource.enabled">
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
              <p>{{ store.isDevHosts ? '可直接调整开发环境兜底文件内容，保存后会写入 hosts.dev。' : '可直接调整当前系统 Hosts 内容，保存后会立即写入目标文件。' }}</p>
            </div>
            <button type="button" class="btn-close hosts-edit-modal-close" @click="showEditModal = false"></button>
          </div>
          <div class="modal-body hosts-edit-modal-body">
            <section class="hosts-edit-form-panel hosts-edit-form-panel-warning">
              <div class="hosts-edit-warning-note">
                <i class="bx bxs-error-alt"></i>
                <div>
                  <strong>{{ store.isDevHosts ? '开发环境写入提醒' : '谨慎修改' }}</strong>
                  <span>{{ store.isDevHosts ? '当前保存目标是开发环境兜底文件，不会直接改系统 Hosts，但仍建议核对域名与 IP 映射。' : '此操作将直接修改系统 Hosts 文件，请确认内容正确后再保存。' }}</span>
                </div>
              </div>
            </section>

            <section class="hosts-edit-form-panel hosts-edit-form-panel-target">
              <div class="hosts-edit-form-panel-head">
                <h6>本次写入目标</h6>
                <span>保存前先确认目标路径、当前模式和备份状态。</span>
              </div>
              <div class="hosts-edit-target-grid">
                <div class="hosts-edit-target-item">
                  <span>目标路径</span>
                  <strong class="mono-text">{{ currentTargetPathLabel }}</strong>
                </div>
                <div class="hosts-edit-target-inline-grid">
                  <div class="hosts-edit-target-item">
                    <span>当前模式</span>
                    <strong>{{ store.isDevHosts ? '开发环境兜底' : '系统 Hosts 直写' }}</strong>
                  </div>
                  <div class="hosts-edit-target-item">
                    <span>备份状态</span>
                    <strong>{{ store.backupEnabled ? '已启用备份' : '未启用备份' }}</strong>
                  </div>
                </div>
              </div>


            </section>

            <section class="hosts-edit-form-panel hosts-edit-form-panel-validation">
              <div class="hosts-edit-form-panel-head">
                <h6>保存前检查</h6>
                <span>先看本次编辑包含多少有效映射、是否有格式错误，以及哪些内容还需要你复查。</span>
              </div>

              <div class="hosts-edit-validation-summary">
                <span class="hosts-edit-check-pill hosts-edit-check-pill-neutral">有效映射 {{ hostsValidation.entryCount }}</span>
                <span class="hosts-edit-check-pill" :class="hostsValidation.errors.length ? 'hosts-edit-check-pill-danger' : 'hosts-edit-check-pill-success'">
                  格式问题 {{ hostsValidation.errors.length }}
                </span>
                <span class="hosts-edit-check-pill" :class="hostsValidation.warnings.length ? 'hosts-edit-check-pill-warning' : 'hosts-edit-check-pill-success'">
                  复查提醒 {{ hostsValidation.warnings.length }}
                </span>
              </div>

              <div class="hosts-validation-grid">
                <div class="hosts-validation-block" :class="hostsValidation.errors.length ? 'hosts-validation-block-danger' : 'hosts-validation-block-success'">
                  <div class="hosts-validation-block-title">
                    <i class="bx" :class="hostsValidation.errors.length ? 'bx-error-circle' : 'bx-check-circle'"></i>
                    <strong>{{ hostsValidation.errors.length ? '发现格式问题' : '未发现格式问题' }}</strong>
                  </div>
                  <ul v-if="hostsValidation.errors.length">
                    <li v-for="item in hostsValidation.errors.slice(0, 4)" :key="`error-${item}`">{{ item }}</li>
                  </ul>
                  <p v-else>当前内容通过基础格式检查，可以继续结合下方差异摘要做人工复核。</p>
                  <p v-if="hostsValidation.errors.length > 4" class="hosts-diff-more">另有 {{ hostsValidation.errors.length - 4 }} 个问题未展开。</p>
                </div>

                <div class="hosts-validation-block" :class="hostsValidation.warnings.length ? 'hosts-validation-block-warning' : 'hosts-validation-block-neutral'">
                  <div class="hosts-validation-block-title">
                    <i class="bx" :class="hostsValidation.warnings.length ? 'bx-error' : 'bx-shield-quarter'"></i>
                    <strong>{{ hostsValidation.warnings.length ? '建议人工复查' : '当前无额外复查项' }}</strong>
                  </div>
                  <ul v-if="hostsValidation.warnings.length">
                    <li v-for="item in hostsValidation.warnings.slice(0, 4)" :key="`warning-${item}`">{{ item }}</li>
                  </ul>
                  <p v-else>当前没有发现重复域名覆盖这类高风险提示。</p>
                  <p v-if="hostsValidation.warnings.length > 4" class="hosts-diff-more">另有 {{ hostsValidation.warnings.length - 4 }} 项提醒未展开。</p>
                </div>
              </div>
              <div class="hosts-edit-combined-divider">
                <h6>本次修改视图</h6>
                <span>按新增、删除、变更三类查看更完整的映射差异。</span>
              </div>

              <div class="hosts-edit-checks-summary">
                <span class="hosts-edit-check-pill hosts-edit-check-pill-success">新增 {{ hostsDiffSummary.added.length }}</span>
                <span class="hosts-edit-check-pill hosts-edit-check-pill-warning">删除 {{ hostsDiffSummary.removed.length }}</span>
                <span class="hosts-edit-check-pill hosts-edit-check-pill-neutral">变更 {{ hostsDiffSummary.changed.length }}</span>
              </div>

              <div v-if="hostsDiffSummary.hasChanges" class="hosts-diff-grid">
                <div v-if="hostsDiffSummary.added.length" class="hosts-edit-check-block hosts-edit-check-block-success">
                  <div class="hosts-edit-check-block-title">
                    <i class="bx bx-plus-circle"></i>
                    <strong>新增映射</strong>
                  </div>
                  <div class="hosts-diff-entry-list">
                    <article v-for="item in visibleAddedDiffItems" :key="`added-${item.host}`" class="hosts-diff-entry-card hosts-diff-entry-card-success">
                      <div class="hosts-diff-entry-head">
                        <span class="hosts-diff-entry-host mono-text">{{ item.host }}</span>
                        <span class="hosts-diff-entry-badge hosts-diff-entry-badge-success">新增</span>
                      </div>
                      <div class="hosts-diff-entry-body hosts-diff-entry-body-single">
                        <div class="hosts-diff-entry-panel">
                          <span class="hosts-diff-entry-label">写入后</span>
                          <code class="hosts-diff-entry-code">{{ item.nextLine }}</code>
                        </div>
                      </div>
                    </article>
                  </div>
                  <div v-if="hostsDiffSummary.added.length > DIFF_PREVIEW_LIMIT" class="hosts-diff-actions">
                    <p class="hosts-diff-more">{{ showAllAddedDiff ? '已展开全部新增映射。' : `另有 ${hostsDiffSummary.added.length - DIFF_PREVIEW_LIMIT} 条新增未展开。` }}</p>
                    <button type="button" class="hosts-inline-link hosts-inline-link-button" @click="showAllAddedDiff = !showAllAddedDiff">
                      {{ showAllAddedDiff ? '收起新增映射' : '展开全部新增映射' }}
                    </button>
                  </div>
                </div>

                <div v-if="hostsDiffSummary.removed.length" class="hosts-edit-check-block hosts-edit-check-block-warning">
                  <div class="hosts-edit-check-block-title">
                    <i class="bx bx-minus-circle"></i>
                    <strong>删除映射</strong>
                  </div>
                  <div class="hosts-diff-entry-list">
                    <article v-for="item in visibleRemovedDiffItems" :key="`removed-${item.host}`" class="hosts-diff-entry-card hosts-diff-entry-card-warning">
                      <div class="hosts-diff-entry-head">
                        <span class="hosts-diff-entry-host mono-text">{{ item.host }}</span>
                        <span class="hosts-diff-entry-badge hosts-diff-entry-badge-warning">删除</span>
                      </div>
                      <div class="hosts-diff-entry-body hosts-diff-entry-body-single">
                        <div class="hosts-diff-entry-panel">
                          <span class="hosts-diff-entry-label">原内容</span>
                          <code class="hosts-diff-entry-code">{{ item.previousLine }}</code>
                        </div>
                      </div>
                    </article>
                  </div>
                  <div v-if="hostsDiffSummary.removed.length > DIFF_PREVIEW_LIMIT" class="hosts-diff-actions">
                    <p class="hosts-diff-more">{{ showAllRemovedDiff ? '已展开全部删除映射。' : `另有 ${hostsDiffSummary.removed.length - DIFF_PREVIEW_LIMIT} 条删除未展开。` }}</p>
                    <button type="button" class="hosts-inline-link hosts-inline-link-button" @click="showAllRemovedDiff = !showAllRemovedDiff">
                      {{ showAllRemovedDiff ? '收起删除映射' : '展开全部删除映射' }}
                    </button>
                  </div>
                </div>

                <div v-if="hostsDiffSummary.changed.length" class="hosts-edit-check-block hosts-edit-check-block-neutral">
                  <div class="hosts-edit-check-block-title">
                    <i class="bx bx-git-compare"></i>
                    <strong>变更映射</strong>
                  </div>
                  <div class="hosts-diff-entry-list">
                    <article v-for="item in visibleChangedDiffItems" :key="`changed-${item.host}`" class="hosts-diff-entry-card hosts-diff-entry-card-neutral">
                      <div class="hosts-diff-entry-head">
                        <span class="hosts-diff-entry-host mono-text">{{ item.host }}</span>
                        <span class="hosts-diff-entry-badge hosts-diff-entry-badge-neutral">变更</span>
                      </div>
                      <div class="hosts-diff-entry-body">
                        <div class="hosts-diff-entry-panel">
                          <span class="hosts-diff-entry-label">变更前</span>
                          <code class="hosts-diff-entry-code">{{ item.previousLine }}</code>
                        </div>
                        <div class="hosts-diff-entry-arrow">
                          <i class="bx bx-right-arrow-alt"></i>
                        </div>
                        <div class="hosts-diff-entry-panel">
                          <span class="hosts-diff-entry-label">变更后</span>
                          <code class="hosts-diff-entry-code">{{ item.nextLine }}</code>
                        </div>
                      </div>
                    </article>
                  </div>
                  <div v-if="hostsDiffSummary.changed.length > DIFF_PREVIEW_LIMIT" class="hosts-diff-actions">
                    <p class="hosts-diff-more">{{ showAllChangedDiff ? '已展开全部变更映射。' : `另有 ${hostsDiffSummary.changed.length - DIFF_PREVIEW_LIMIT} 条变更未展开。` }}</p>
                    <button type="button" class="hosts-inline-link hosts-inline-link-button" @click="showAllChangedDiff = !showAllChangedDiff">
                      {{ showAllChangedDiff ? '收起变更映射' : '展开全部变更映射' }}
                    </button>
                  </div>
                </div>
              </div>

              <div v-else class="hosts-edit-check-block hosts-edit-check-block-neutral">
                <div class="hosts-edit-check-block-title">
                  <i class="bx bx-equalizer"></i>
                  <strong>当前尚无差异</strong>
                </div>
                <p>你还没有改动任何映射，或当前改动只影响注释与空行。</p>
              </div>
            </section>

            <section class="hosts-edit-form-panel hosts-edit-form-panel-editor">
              <div class="hosts-edit-form-panel-head">
                <h6>Hosts 内容</h6>
                <span>支持多行编辑，建议保留原有结构与注释格式；这里的保存会直接覆盖当前目标文件内容，不会重新拉取源。</span>
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
              <span>建议保存前先检查域名与 IP 映射格式；此处保存会直接写入当前目标文件，不会重新拉取源。</span>
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
import { ref, onMounted, reactive, watch, computed } from 'vue';
import { useHostsStore, type HostsSource } from '@/stores/modules/hosts';
import { useMobile } from '@/composables/useMobile';
import { useToast } from '@/composables/useToast';
import { useConfirm } from '@/composables/useConfirm';
import PageEmptyState from '@/components/shared/PageEmptyState.vue';
import PageHeaderShell from '@/components/shared/PageHeaderShell.vue';
import { getErrorMessage } from '@/utils/error';


const store = useHostsStore();
const { isMobile } = useMobile();
const toast = useToast();
const { confirm } = useConfirm();

const showAddModal = ref(false);
const showEditModal = ref(false);
const adding = ref(false);
const isEditing = ref(false);
const editingSourceId = ref('');

const saving = ref(false);
const editingContent = ref('');
const togglingSourceKeys = ref<Set<string>>(new Set());
const showAllAddedDiff = ref(false);
const showAllRemovedDiff = ref(false);
const showAllChangedDiff = ref(false);

const DIFF_PREVIEW_LIMIT = 6;



const newSource = reactive<HostsSource>({
  name: '',
  url: '',
  enabled: true
});

const currentTargetPathLabel = computed(() => store.currentHostsPath || (store.isDevHosts ? 'hosts.dev' : '未读取到目标路径'));

const hostsPreviewTitle = computed(() => store.isDevHosts ? '当前开发环境 Hosts' : '当前系统 Hosts');

const hostsPreviewDescription = computed(() => store.isDevHosts
  ? '预览当前开发环境兜底文件内容；进入编辑模式后保存会直接写入 hosts.dev，不会重新拉取源或触发重建。'
  : '预览当前系统 Hosts 文件内容；进入编辑模式后保存会直接写入目标文件，不会重新拉取源或触发重建。');



onMounted(async () => {
  await store.fetchSources();
  await store.fetchContent();
});

watch(showEditModal, (val) => {
  if (val) {
    editingContent.value = store.currentHosts;
    showAllAddedDiff.value = false;
    showAllRemovedDiff.value = false;
    showAllChangedDiff.value = false;
  }
});

const toggleSource = async (source: HostsSource) => {
  const sourceKey = source.id || source.url;
  if (!source.id) {
    toast.error('源 ID 缺失，无法更新');
    return;
  }
  if (isSourceToggling(sourceKey)) return;

  const nextEnabled = !source.enabled;
  togglingSourceKeys.value = new Set(togglingSourceKeys.value).add(sourceKey);
  try {
    await store.updateSource(source.id, { enabled: nextEnabled });
    if (nextEnabled) {
      toast.success(`已启用源“${source.name}”`);
    } else {
      toast.success(`已关闭源“${source.name}”，后台正在重建 Hosts`);
    }
  } catch (e) {
    toast.error('更新失败');
    store.fetchSources();
  } finally {
    const next = new Set(togglingSourceKeys.value);
    next.delete(sourceKey);
    togglingSourceKeys.value = next;
  }
};

const isSourceToggling = (key: string) => togglingSourceKeys.value.has(key);


const confirmDelete = async (source: HostsSource) => {
  if (await confirm(`确定要删除 ${source.name} 吗？`, '删除确认')) {
    try {
      await store.deleteSource(source.id!);
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
      const editingSource = store.sources.find((source) => source.id === editingSourceId.value);
      if (!editingSource?.id) {
        throw new Error('未找到要编辑的 Hosts 源');
      }

      if (editingSource.url !== newSource.url) {
        await store.deleteSource(editingSource.id);
        await store.addSource({ ...newSource });
      } else {
        await store.updateSource(editingSource.id, { ...newSource });
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
  editingSourceId.value = source.id || '';
  newSource.name = source.name;
  newSource.url = source.url;
  newSource.enabled = source.enabled;
  showAddModal.value = true;
};

const resetForm = () => {
  newSource.name = '';
  newSource.url = '';
  newSource.enabled = true;
  isEditing.value = false;
  editingSourceId.value = '';
};

watch(showAddModal, (val) => {
  if (!val) {
    resetForm();
  }
});



const isLikelyIpv4 = (value: string) => {
  const parts = value.split('.');
  if (parts.length !== 4) return false;
  return parts.every((part) => /^\d+$/.test(part) && Number(part) >= 0 && Number(part) <= 255);
};

const isLikelyIpv6 = (value: string) => /^[0-9a-fA-F:]+$/.test(value) && value.includes(':');

const isLikelyHostsIp = (value: string) => isLikelyIpv4(value) || isLikelyIpv6(value);

const isLikelyHostname = (value: string) => /^(localhost|[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9])$/.test(value);

const hostsValidation = computed(() => {
  const errors: string[] = [];
  const warnings: string[] = [];
  const hostToIpMap = new Map<string, string>();
  let entryCount = 0;

  const lines = editingContent.value.split(/\r?\n/);

  lines.forEach((line, index) => {
    const lineNumber = index + 1;
    const trimmed = line.trim();

    if (!trimmed || trimmed.startsWith('#')) return;

    const withoutComment = trimmed.replace(/\s+#.*$/, '').trim();
    if (!withoutComment) return;

    const parts = withoutComment.split(/\s+/).filter(Boolean);
    if (parts.length < 2) {
      errors.push(`第 ${lineNumber} 行缺少域名映射，Hosts 记录至少需要“IP + 域名”。`);
      return;
    }

    const [ip = '', ...hosts] = parts;

    if (!isLikelyHostsIp(ip)) {
      errors.push(`第 ${lineNumber} 行的 IP 格式看起来不合法：${ip}`);
      return;
    }

    const invalidHosts = hosts.filter((host) => !isLikelyHostname(host));
    if (invalidHosts.length) {
      errors.push(`第 ${lineNumber} 行包含可疑域名：${invalidHosts.join('、')}`);
      return;
    }

    entryCount += 1;

    hosts.forEach((host) => {
      const previousIp = hostToIpMap.get(host);
      if (previousIp && previousIp !== ip) {
        warnings.push(`域名 ${host} 同时指向 ${previousIp} 和 ${ip}，请确认是否为有意覆盖。`);
        return;
      }
      hostToIpMap.set(host, ip);
    });
  });

  return {
    entryCount,
    errors: Array.from(new Set(errors)),
    warnings: Array.from(new Set(warnings)),
  };
});

type ParsedHostsEntry = {
  host: string;
  ip: string;
  line: string;
};

type HostsDiffItem = {
  host: string;
  previousIp?: string;
  nextIp?: string;
  previousLine?: string;
  nextLine?: string;
};

const parseHostsEntries = (content: string) => {
  const entryMap = new Map<string, ParsedHostsEntry>();

  content.split(/\r?\n/).forEach((line) => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) return;

    const withoutComment = trimmed.replace(/\s+#.*$/, '').trim();
    if (!withoutComment) return;

    const parts = withoutComment.split(/\s+/).filter(Boolean);
    if (parts.length < 2) return;

    const [ip = '', ...hosts] = parts;
    if (!isLikelyHostsIp(ip)) return;

    hosts.filter((host) => isLikelyHostname(host)).forEach((host) => {
      entryMap.set(host, {
        host,
        ip,
        line: `${ip} ${host}`,
      });
    });
  });

  return entryMap;
};

const hostsDiffSummary = computed(() => {
  const originalMap = parseHostsEntries(store.currentHosts || '');
  const editedMap = parseHostsEntries(editingContent.value);

  const added: HostsDiffItem[] = [];
  const removed: HostsDiffItem[] = [];
  const changed: HostsDiffItem[] = [];

  editedMap.forEach((entry, host) => {
    const originalEntry = originalMap.get(host);
    if (!originalEntry) {
      added.push({
        host,
        nextIp: entry.ip,
        nextLine: entry.line,
      });
      return;
    }

    if (originalEntry.ip !== entry.ip) {
      changed.push({
        host,
        previousIp: originalEntry.ip,
        nextIp: entry.ip,
        previousLine: originalEntry.line,
        nextLine: entry.line,
      });
    }
  });

  originalMap.forEach((entry, host) => {
    if (!editedMap.has(host)) {
      removed.push({
        host,
        previousIp: entry.ip,
        previousLine: entry.line,
      });
    }
  });

  return {
    added,
    removed,
    changed,
    hasChanges: added.length > 0 || removed.length > 0 || changed.length > 0,
  };
});

const visibleAddedDiffItems = computed(() => (
  showAllAddedDiff.value ? hostsDiffSummary.value.added : hostsDiffSummary.value.added.slice(0, DIFF_PREVIEW_LIMIT)
));

const visibleRemovedDiffItems = computed(() => (
  showAllRemovedDiff.value ? hostsDiffSummary.value.removed : hostsDiffSummary.value.removed.slice(0, DIFF_PREVIEW_LIMIT)
));

const visibleChangedDiffItems = computed(() => (
  showAllChangedDiff.value ? hostsDiffSummary.value.changed : hostsDiffSummary.value.changed.slice(0, DIFF_PREVIEW_LIMIT)
));

const handleSaveHosts = async () => {
  const originalContent = store.currentHosts || '';
  const nextContent = editingContent.value;

  if (nextContent === originalContent) {
    toast.info('Hosts 内容未变化，无需保存');
    return;
  }

  if (hostsValidation.value.errors.length) {
    toast.error(`发现 ${hostsValidation.value.errors.length} 个格式问题，请先修正后再保存`);
    return;
  }

  if (hostsValidation.value.warnings.length) {
    const warningConfirmed = await confirm(
      `当前发现 ${hostsValidation.value.warnings.length} 项需要复查的内容，例如重复域名映射。确认已经检查后再继续保存吗？`,
      '保存前复查提醒'
    );
    if (!warningConfirmed) return;
  }

  const primaryMessage = store.isDevHosts
    ? '确定要保存当前修改吗？这会写入开发环境兜底文件 hosts.dev。'
    : '确定要保存当前修改吗？这会立即写入目标 Hosts 文件并影响当前系统解析。';

  if (!await confirm(primaryMessage, '保存 Hosts 确认')) return;

  if (!store.isDevHosts) {
    const secondaryConfirmed = await confirm(
      '再次确认：你正在直接修改系统 Hosts。错误内容可能导致域名解析异常，请确认你已检查 IP、域名和注释格式。',
      '高风险操作确认'
    );
    if (!secondaryConfirmed) return;
  }

  saving.value = true;
  try {
    await store.saveHostsContent(nextContent);
    await store.fetchContent();
    showEditModal.value = false;
    toast.success(store.isDevHosts ? '开发环境 Hosts 已保存' : '系统 Hosts 已保存');
  } catch (e: any) {
    toast.error('保存失败: ' + getErrorMessage(e, '未知错误'));
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
  gap: 1.25rem;
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

.hosts-path-meta {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  flex-wrap: wrap;
  margin-top: 0.75rem;
}

.hosts-path-badge {
  display: inline-flex;
  align-items: center;
  min-height: 1.9rem;
  padding: 0.32rem 0.72rem;
  border-radius: 999px;
  background: rgba(var(--primary-rgb), 0.08);
  border: 1px solid rgba(var(--primary-rgb), 0.16);
  color: var(--primary-color);
  font-size: 0.76rem;
  font-weight: 600;
  line-height: 1.4;
  word-break: break-all;
}

.hosts-path-badge-dev {
  background: rgba(40, 167, 69, 0.1);
  border-color: rgba(40, 167, 69, 0.18);
  color: #1f9d55;
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

.hosts-preview-meta-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.8rem;
}

.hosts-preview-meta-card {
  padding: 0.95rem 1rem;
  border-radius: 0.95rem;
  border: 1px solid rgba(161, 172, 184, 0.14);
  background: color-mix(in srgb, var(--bg-surface-alt) 72%, transparent);
  min-width: 0;
}

.hosts-preview-meta-label {
  display: inline-block;
  margin-bottom: 0.38rem;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.03em;
}

.hosts-preview-meta-card strong {
  display: block;
  color: var(--text-heading);
  font-size: 0.86rem;
  line-height: 1.5;
  word-break: break-word;
}

.hosts-preview-meta-card p {
  margin: 0.4rem 0 0;
  color: var(--text-muted);
  font-size: 0.79rem;
  line-height: 1.55;
}

.hosts-preview-note-safe {
  background: rgba(40, 167, 69, 0.08);
  border-color: rgba(40, 167, 69, 0.16);
  color: #1f8f4d;
}

.hosts-preview-note-safe i,
.hosts-preview-note-safe span {
  color: #1f8f4d;
}

.hosts-preview-note-danger {
  background: rgba(255, 193, 7, 0.08);
  border-color: rgba(255, 193, 7, 0.16);
  color: #b7791f;
}

.hosts-preview-note-danger i,
.hosts-preview-note-danger span {
  color: #b7791f;
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
  background: rgba(var(--primary-rgb), 0.04);
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
  max-width: min(94vw, 82rem);
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
  display: grid;
  grid-template-columns: minmax(19rem, 0.9fr) minmax(28rem, 1.45fr);
  grid-template-areas:
    "warning editor"
    "target editor"
    "validation editor";
  align-items: stretch;
  gap: 0.9rem;
  padding: 0.95rem 1.05rem;
  max-height: min(72vh, 48rem);
  overflow: auto;
}


.hosts-edit-form-panel {
  padding: 0.78rem 0.82rem;
  border: 1px solid rgba(161, 172, 184, 0.14);
  border-radius: 0.95rem;
  background: color-mix(in srgb, var(--bg-surface-alt) 58%, transparent);
}

.hosts-edit-form-panel-warning {
  grid-area: warning;
  border-color: rgba(255, 193, 7, 0.34);
  background: color-mix(in srgb, rgba(255, 193, 7, 0.18) 100%, var(--bg-surface));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.16);
}

.hosts-edit-form-panel-target {
  grid-area: target;
  background: rgba(var(--primary-rgb), 0.05);
}

.hosts-edit-form-panel-validation {
  grid-area: validation;
}

.hosts-edit-form-panel-editor {
  grid-area: editor;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  align-self: stretch;
}

.hosts-edit-textarea-shell {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
}

.hosts-edit-textarea {
  flex: 1 1 auto;
  min-height: 0;
  height: auto;
  resize: vertical;
}


.hosts-edit-combined-divider {
  margin: 0.85rem 0 0.62rem;
  padding-top: 0.78rem;
  border-top: 1px dashed rgba(161, 172, 184, 0.22);
}

.hosts-edit-combined-divider h6 {
  margin: 0;
  color: var(--text-heading);
  font-size: 0.9rem;
  font-weight: 700;
}

.hosts-edit-combined-divider span {
  display: block;
  margin-top: 0.2rem;
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.45;
}



.hosts-edit-target-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.55rem;
}


.hosts-edit-target-inline-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.55rem;
}


.hosts-edit-target-item {
  padding: 0.72rem 0.78rem;
  border-radius: 0.82rem;
  border: 1px solid rgba(161, 172, 184, 0.14);
  background: rgba(var(--primary-rgb), 0.04);
  min-width: 0;
}

.hosts-edit-target-item span {
  display: block;
  margin-bottom: 0.28rem;
  color: var(--text-muted);
  font-size: 0.74rem;
  line-height: 1.4;
}

.hosts-edit-target-item strong {
  display: block;
  color: var(--text-heading);
  font-size: 0.83rem;
  line-height: 1.5;
  word-break: break-word;
}



.hosts-inline-link {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  color: var(--primary-color);
  font-size: 0.79rem;
  font-weight: 600;
  line-height: 1.45;
  text-decoration: none;
  transition: color var(--transition-fast), opacity var(--transition-fast);
}

.hosts-inline-link:hover,
.hosts-inline-link:focus-visible {
  color: var(--primary-hover);
  opacity: 0.92;
}

.hosts-inline-link-button {
  padding: 0;
  border: 0;
  background: transparent;
  cursor: pointer;
}

.hosts-diff-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  margin-top: 0.5rem;
}

.hosts-diff-actions .hosts-diff-more {
  margin: 0;
}

.hosts-inline-link-button:hover,
.hosts-inline-link-button:focus-visible {
  background: color-mix(in srgb, var(--bg-surface-alt) 60%, rgba(var(--primary-rgb), 0.03));
}

.hosts-edit-validation-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.45rem;
  margin-bottom: 0.72rem;
}

.hosts-edit-checks-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.45rem;
  margin-bottom: 0.62rem;
}

.hosts-edit-check-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2rem;
  width: 100%;
  padding: 0.38rem 0.55rem;
  border: 1px solid rgba(161, 172, 184, 0.16);
  border-radius: 999px;
  background: color-mix(in srgb, var(--bg-surface-alt) 74%, transparent);
  color: var(--text-muted);
  font-size: 0.78rem;
  font-weight: 700;
  line-height: 1.2;
  white-space: nowrap;
}

.hosts-edit-check-pill-success {
  border-color: rgba(40, 167, 69, 0.22);
  background: rgba(40, 167, 69, 0.12);
  color: #1f8f4d;
}

.hosts-edit-check-pill-warning {
  border-color: rgba(255, 193, 7, 0.26);
  background: rgba(255, 193, 7, 0.12);
  color: #b56a00;
}

.hosts-edit-check-pill-neutral {
  border-color: rgba(var(--primary-rgb), 0.18);
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
}

.hosts-diff-grid {
  display: grid;
  gap: 0.62rem;
}

.hosts-edit-check-block {
  padding: 0.72rem;
  border: 1px solid rgba(161, 172, 184, 0.14);
  border-radius: 0.9rem;
  background: rgba(var(--bg-surface-rgb), 0.56);
}

.hosts-edit-check-block-success {
  border-color: rgba(40, 167, 69, 0.2);
  background: rgba(40, 167, 69, 0.08);
}

.hosts-edit-check-block-warning {
  border-color: rgba(255, 193, 7, 0.24);
  background: rgba(255, 193, 7, 0.08);
}

.hosts-edit-check-block-neutral {
  border-color: rgba(var(--primary-rgb), 0.14);
  background: rgba(var(--primary-rgb), 0.07);
}

.hosts-edit-check-block-title {
  display: flex;
  align-items: center;
  gap: 0.42rem;
  margin-bottom: 0.55rem;
  color: var(--text-heading);
}

.hosts-edit-check-block-title i {
  flex: 0 0 auto;
  font-size: 1rem;
}

.hosts-edit-check-block-success .hosts-edit-check-block-title i,
.hosts-edit-check-block-success .hosts-edit-check-block-title strong {
  color: #1f8f4d;
}

.hosts-edit-check-block-warning .hosts-edit-check-block-title i,
.hosts-edit-check-block-warning .hosts-edit-check-block-title strong {
  color: #b56a00;
}

.hosts-edit-check-block-neutral .hosts-edit-check-block-title i,
.hosts-edit-check-block-neutral .hosts-edit-check-block-title strong {
  color: var(--primary-color);
}

.hosts-edit-check-block-title strong {
  font-size: 0.84rem;
  font-weight: 800;
}

.hosts-edit-check-block p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.79rem;
  line-height: 1.55;
}

.hosts-diff-entry-list {
  display: grid;
  gap: 0.48rem;
}

.hosts-diff-entry-card {
  padding: 0.58rem;
  border: 1px solid rgba(161, 172, 184, 0.12);
  border-radius: 0.76rem;
  background: rgba(var(--bg-surface-rgb), 0.72);
}

.hosts-diff-entry-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.45rem;
}

.hosts-diff-entry-host {
  min-width: 0;
  color: var(--text-heading);
  font-size: 0.78rem;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hosts-diff-entry-badge {
  flex: 0 0 auto;
  padding: 0.16rem 0.42rem;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 800;
  line-height: 1.2;
}

.hosts-diff-entry-badge-success {
  background: rgba(40, 167, 69, 0.12);
  color: #1f8f4d;
}

.hosts-diff-entry-badge-warning {
  background: rgba(255, 193, 7, 0.14);
  color: #b56a00;
}

.hosts-diff-entry-badge-neutral {
  background: rgba(var(--primary-rgb), 0.12);
  color: var(--primary-color);
}

.hosts-diff-entry-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  align-items: stretch;
  gap: 0.45rem;
}

.hosts-diff-entry-body-single {
  grid-template-columns: 1fr;
}

.hosts-diff-entry-panel {
  min-width: 0;
  padding: 0.46rem 0.5rem;
  border-radius: 0.62rem;
  background: color-mix(in srgb, var(--bg-surface-alt) 70%, transparent);
  border: 1px solid rgba(161, 172, 184, 0.1);
}

.hosts-diff-entry-label {
  display: block;
  margin-bottom: 0.24rem;
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.03em;
}

.hosts-diff-entry-code {
  display: block;
  color: var(--text-heading);
  font-size: 0.75rem;
  line-height: 1.45;
  white-space: pre-wrap;
  word-break: break-all;
  background: transparent;
}

.hosts-diff-entry-arrow {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
  font-size: 1rem;
}


.hosts-edit-check-pill-danger {
  background: rgba(225, 108, 108, 0.12);
  color: var(--danger-color);
  border-color: rgba(225, 108, 108, 0.2);
}


.hosts-validation-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.55rem;
}


.hosts-validation-block {
  padding: 0.78rem 0.82rem;
  border-radius: 0.9rem;
  border: 1px solid rgba(161, 172, 184, 0.14);
  background: rgba(var(--bg-surface-rgb), 0.52);
}

.hosts-validation-block-title {
  display: flex;
  align-items: center;
  gap: 0.42rem;
  margin-bottom: 0.45rem;
}

.hosts-validation-block-title i {
  flex: 0 0 auto;
  font-size: 1rem;
}

.hosts-validation-block-title strong {
  color: var(--text-heading);
  font-size: 0.84rem;
}

.hosts-validation-block ul {
  margin: 0;
  padding-left: 1.05rem;
}

.hosts-validation-block li,
.hosts-validation-block p {
  color: var(--text-muted);
  font-size: 0.79rem;
  line-height: 1.55;
}

.hosts-validation-block p {
  margin: 0;
}

.hosts-validation-block-danger {
  border-color: rgba(225, 108, 108, 0.22);
  background: rgba(225, 108, 108, 0.08);
}

.hosts-validation-block-danger .hosts-validation-block-title i,
.hosts-validation-block-danger .hosts-validation-block-title strong {
  color: var(--danger-color);
}

.hosts-validation-block-warning {
  border-color: rgba(255, 193, 7, 0.24);
  background: rgba(255, 193, 7, 0.08);
}

.hosts-validation-block-warning .hosts-validation-block-title i,
.hosts-validation-block-warning .hosts-validation-block-title strong {
  color: #b56a00;
}

.hosts-validation-block-success {
  border-color: rgba(40, 167, 69, 0.2);
  background: rgba(40, 167, 69, 0.08);
}

.hosts-validation-block-success .hosts-validation-block-title i,
.hosts-validation-block-success .hosts-validation-block-title strong {
  color: #1f8f4d;
}

.hosts-validation-block-neutral {
  background: color-mix(in srgb, var(--bg-surface-alt) 68%, transparent);
}


.hosts-edit-warning-note {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
}

.hosts-edit-warning-note > div {
  min-width: 0;
  color: #b56a00;
}


.hosts-edit-warning-note i {
  color: #b56a00;
  font-size: 1.1rem;
  flex-shrink: 0;
  margin-top: 0.08rem;
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
  flex: 1 1 auto;
  min-height: 0;
  border: 1px solid var(--border-color);
  border-radius: 0.95rem;
  overflow: hidden;
  background: var(--bg-surface);
}

.hosts-edit-textarea {
  min-height: 38rem;
  height: 100%;
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

@media (max-width: 1100px) {
  .hosts-edit-modal-dialog {
    max-width: min(96vw, 54rem);
  }

  .hosts-edit-modal-body {
    grid-template-columns: 1fr;
    grid-template-areas:
      "warning"
      "target"
      "validation"
      "editor";
    max-height: 76vh;
  }

  .hosts-edit-textarea {
    min-height: 24rem;
  }
}

@media (max-width: 720px) {
  .hosts-edit-modal-dialog {
    max-width: 100vw;
    margin: 0.5rem auto;
    padding: 0.5rem;
  }

  .hosts-edit-modal-body {
    padding: 0.75rem;
    max-height: 72vh;
  }

  .hosts-edit-target-inline-grid {
    grid-template-columns: 1fr;
  }

  .hosts-edit-validation-summary,
  .hosts-edit-checks-summary {
    grid-template-columns: 1fr;
  }

  .hosts-edit-modal-footer {
    align-items: stretch;
    flex-direction: column;
  }

  .hosts-edit-modal-footer-actions {
    justify-content: flex-end;
  }
}

.switch {
  --switch-width: 46px;
  --switch-height: 24px;
  --switch-bg: rgba(161, 172, 184, 0.42);
  --switch-checked-bg: var(--success-color);
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

  .hosts-preview-meta-grid,
  .hosts-edit-target-grid,
  .hosts-validation-grid {
    grid-template-columns: 1fr;
  }

  .hosts-edit-target-explainer-body,
  .hosts-diff-actions {
    width: 100%;
  }

  .hosts-diff-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .hosts-inline-link-button {
    justify-content: flex-start;
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
