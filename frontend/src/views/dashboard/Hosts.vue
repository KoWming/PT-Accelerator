<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">Hosts源管理</h2>
    </div>
    
    <!-- Hosts Source List -->
    <div class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Hosts源列表</h5>
        <button class="btn-pill btn-pill-primary" @click="showAddModal = true">
          <i class="bi bi-plus-lg me-1"></i>添加源
        </button>
      </div>
      <div class="card-body">
        <div v-if="store.loading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else-if="store.sources.length === 0" class="text-center py-4 text-muted">
          暂无 Hosts 源
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle" style="--bs-table-bg: transparent; --bs-table-accent-bg: transparent;">
            <thead>
              <tr>
                <th style="width: 1%; white-space: nowrap;">名称</th>
                <th>URL</th>
                <th class="text-center" style="width: 100px;">状态</th>
                <th class="text-center" style="width: 180px;">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="source in store.sources" :key="source.url">
                <td style="white-space: nowrap;">{{ source.name }}</td>
                <td class="text-truncate font-monospace" style="max-width: 300px; font-weight: 400 !important; font-size: 0.85rem;" :title="source.url">{{ source.url }}</td>
                <td class="text-center">
                  <label class="switch">
                      <input type="checkbox" :checked="source.enable" @change="toggleSource(source)">
                      <div class="slider">
                          <div class="circle">
                              <svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg">
                                  <g>
                                      <path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path>
                                  </g>
                              </svg>
                              <svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg">
                                  <g>
                                      <path class="" data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path>
                                  </g>
                              </svg>
                          </div>
                      </div>
                  </label>
                </td>
                <td class="text-center">
                  <div class="d-flex flex-wrap gap-2 justify-content-center">
                    <button class="btn-pill btn-pill-primary btn-sm" style="padding: 0.25rem 0.5rem; font-size: 0.75rem; white-space: nowrap;" @click="openEditModal(source)">
                      <i class="bi bi-pencil"></i> 编辑
                    </button>
                    <button class="btn-pill btn-pill-danger btn-sm" style="padding: 0.25rem 0.5rem; font-size: 0.75rem; white-space: nowrap;" @click="confirmDelete(source)">
                      <i class="bi bi-trash"></i> 删除
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Current Hosts Content -->
    <div class="card overflow-hidden">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">当前系统Hosts</h5>
        <button class="btn-pill btn-pill-warning" @click="showEditModal = true">
          <i class="bi bi-pencil me-1"></i>编辑Hosts
        </button>
      </div>
      <div class="card-body">
        <pre class="mb-0 hosts-content" style="max-height: 400px; overflow-y: auto;">{{ store.currentHosts || '正在加载...' }}</pre>
      </div>
    </div>

    <!-- Add Modal -->
    <div v-if="showAddModal" class="modal fade show d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? '编辑 Hosts 源' : '添加 Hosts 源' }}</h5>
            <button type="button" class="btn-close" @click="showAddModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="handleAddSource">
              <div class="mb-3">
                <label class="form-label">名称 <span class="text-danger">*</span></label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-tag"></i></span>
                  <input type="text" class="form-control" v-model="newSource.name" required>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">URL <span class="text-danger">*</span></label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-link-45deg"></i></span>
                  <input type="url" class="form-control" v-model="newSource.url" required>
                </div>
              </div>
              <div class="form-check mb-3">
                <input class="form-check-input" type="checkbox" v-model="newSource.enable">
                <label class="form-check-label">启用</label>
              </div>
              <div class="text-end">
                <button type="button" class="btn btn-secondary me-2" @click="showAddModal = false">取消</button>
                <button type="submit" class="btn btn-primary" :disabled="adding">
                  <span v-if="adding" class="spinner-border spinner-border-sm me-1"></span>
                  {{ isEditing ? '保存' : '添加' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Hosts Modal -->
    <div v-if="showEditModal" class="modal fade show d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">编辑 Hosts</h5>
            <button type="button" class="btn-close" @click="showEditModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-warning">
              <i class="bi bi-exclamation-triangle me-2"></i>
              此操作将直接修改系统 Hosts 文件，请谨慎操作！
            </div>
            <textarea class="form-control font-monospace" rows="15" v-model="editingContent"></textarea>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showEditModal = false">取消</button>
            <button type="button" class="btn btn-primary" @click="handleSaveHosts" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              保存
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, watch } from 'vue';
import { useHostsStore, type HostsSource } from '../../stores/hosts';
import { useToast } from 'vue-toastification';
import { useConfirm } from '../../composables/useConfirm';

const store = useHostsStore();
const toast = useToast();
const { confirm } = useConfirm();

const showAddModal = ref(false);
const showEditModal = ref(false);
const adding = ref(false);
const isEditing = ref(false);
const editingSourceUrl = ref('');

const saving = ref(false);
const editingContent = ref('');

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
  try {
    await store.updateSource(source.url, { enable: !source.enable });
  } catch (e) {
    toast.error('更新失败');
    store.fetchConfig();
  }
};

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
  .switch {
    /* switch */
    --switch-width: 36px;
    --switch-height: 20px;
    --switch-bg: var(--secondary-color);
    --switch-checked-bg: var(--success-color);
    --switch-offset: calc((var(--switch-height) - var(--circle-diameter)) / 2);
    --switch-transition: all .2s cubic-bezier(0.27, 0.2, 0.25, 1.51);
    /* circle */
    --circle-diameter: 14px;
    --circle-bg: #fff;
    --circle-shadow: 1px 1px 2px rgba(146, 146, 146, 0.45);
    --circle-checked-shadow: -1px 1px 2px rgba(163, 163, 163, 0.45);
    --circle-transition: var(--switch-transition);
    /* icon */
    --icon-transition: all .2s cubic-bezier(0.27, 0.2, 0.25, 1.51);
    --icon-cross-color: var(--switch-bg);
    --icon-cross-size: 5px;
    --icon-checkmark-color: var(--switch-checked-bg);
    --icon-checkmark-size: 8px;
    /* effect line */
    --effect-width: calc(var(--circle-diameter) / 2);
    --effect-height: calc(var(--effect-width) / 2 - 1px);
    --effect-bg: var(--circle-bg);
    --effect-border-radius: 1px;
    --effect-transition: all .2s ease-in-out;
  }

  .switch input {
    display: none;
  }

  .switch {
    display: inline-block;
  }

  .switch svg {
    -webkit-transition: var(--icon-transition);
    -o-transition: var(--icon-transition);
    transition: var(--icon-transition);
    position: absolute;
    top: 50%;
    left: 50%;
    height: auto;
  }

  .switch .checkmark {
    width: var(--icon-checkmark-size);
    color: var(--icon-checkmark-color);
    -webkit-transform: translate(-50%, -50%) scale(0);
    -ms-transform: translate(-50%, -50%) scale(0);
    transform: translate(-50%, -50%) scale(0);
  }

  .switch .cross {
    width: var(--icon-cross-size);
    color: var(--icon-cross-color);
    -webkit-transform: translate(-50%, -50%) scale(1);
    -ms-transform: translate(-50%, -50%) scale(1);
    transform: translate(-50%, -50%) scale(1);
  }

  .slider {
    -webkit-box-sizing: border-box;
    box-sizing: border-box;
    width: var(--switch-width);
    height: var(--switch-height);
    background: var(--switch-bg);
    border-radius: 999px;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    position: relative;
    -webkit-transition: var(--switch-transition);
    -o-transition: var(--switch-transition);
    transition: var(--switch-transition);
    cursor: pointer;
  }

  .circle {
    width: var(--circle-diameter);
    height: var(--circle-diameter);
    background: var(--circle-bg);
    border-radius: inherit;
    -webkit-box-shadow: var(--circle-shadow);
    box-shadow: var(--circle-shadow);
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    -webkit-box-pack: center;
    -ms-flex-pack: center;
    justify-content: center;
    -webkit-transition: var(--circle-transition);
    -o-transition: var(--circle-transition);
    transition: var(--circle-transition);
    z-index: 1;
    position: absolute;
    left: var(--switch-offset);
  }

  .slider::before {
    content: "";
    position: absolute;
    width: var(--effect-width);
    height: var(--effect-height);
    left: calc(var(--switch-offset) + (var(--effect-width) / 2));
    background: var(--effect-bg);
    border-radius: var(--effect-border-radius);
    -webkit-transition: var(--effect-transition);
    -o-transition: var(--effect-transition);
    transition: var(--effect-transition);
  }

  /* actions */

  .switch input:checked+.slider {
    background: var(--switch-checked-bg);
  }

  .switch input:checked+.slider .checkmark {
    -webkit-transform: translate(-50%, -50%) scale(1);
    -ms-transform: translate(-50%, -50%) scale(1);
    transform: translate(-50%, -50%) scale(1);
  }

  .switch input:checked+.slider .cross {
    -webkit-transform: translate(-50%, -50%) scale(0);
    -ms-transform: translate(-50%, -50%) scale(0);
    transform: translate(-50%, -50%) scale(0);
  }

  .switch input:checked+.slider::before {
    left: calc(100% - var(--effect-width) - (var(--effect-width) / 2) - var(--switch-offset));
  }

  .switch input:checked+.slider .circle {
    left: calc(100% - var(--circle-diameter) - var(--switch-offset));
    -webkit-box-shadow: var(--circle-checked-shadow);
    box-shadow: var(--circle-checked-shadow);
  }
</style>
