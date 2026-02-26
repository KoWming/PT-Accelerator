<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">Trackers管理</h2>
      <Teleport to="#mobile-header-actions" :disabled="!isMobile">
        <div v-if="isMobile || true">


        </div>
      </Teleport>
    </div>

    <!-- Function Management Card -->
    <div class="card mb-4">
      <div class="card-header">
        <h5 class="card-title mb-0">功能操作</h5>
      </div>
      <div class="card-body">
        <div class="row g-3">
          <!-- Left Column: Batch Update IP -->
          <div class="col-md-6 border-end-md">
            <label class="form-label fw-bold">批量更新IP</label>
            <div class="input-group">
              <span class="input-group-text">新IP地址</span>
              <input type="text" class="form-control" v-model="batchIp" placeholder="例如: 1.1.1.1">
              <button class="btn btn-action-primary" @click="handleBatchUpdateIp" :disabled="batchIpUpdating || !batchIp || !isValidIpv4">
                <span v-if="batchIpUpdating" class="spinner-border spinner-border-sm me-1"></span>
                确认修改
              </button>
            </div>
            <div class="form-text text-muted mt-2">
              <i class="bi bi-info-circle me-1"></i>
              此操作将把所有Tracker的IP修改为指定值。
            </div>
          </div>
          
          <!-- Right Column: Other Actions -->
          <div class="col-md-6 d-flex align-items-center justify-content-center">
            <div class="row g-2 w-100">
              <div class="col-6">
                <button class="btn-pill btn-pill-primary w-100 text-nowrap px-1" @click="showAddModal = true">
                  <span>
                    <i class="bi bi-plus-lg me-1"></i> 添加Tracker
                  </span>
                </button>
              </div>
              <div class="col-6">
                <button class="btn-pill btn-pill-teal w-100 text-nowrap px-1" @click="showBatchModal = true">
                  <span>
                    <i class="bi bi-list-check me-1"></i> 批量添加
                  </span>
                </button>
              </div>
              <div class="col-6">
                <button class="btn-pill btn-pill-success w-100 text-nowrap px-1" @click="handleRunIpOptimization" :disabled="optimizing">
                  <span>
                    <span v-if="optimizing" class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-lightning-charge me-1"></i> 运行IP优选
                  </span>
                </button>
              </div>
              <div class="col-6">
                <button class="btn-pill btn-pill-warning w-100 text-nowrap px-1" @click="openWhitelistModal">
                  <span>
                    <i class="bi bi-shield-check me-1"></i> 白名单操作
                  </span>
                </button>
              </div>
              <div class="col-12">
                <button class="btn-pill btn-pill-danger w-100 text-nowrap px-1" @click="handleClearAllTrackers" :disabled="clearing">
                  <span>
                    <span v-if="clearing" class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-trash me-1"></i> 清空当前Tracker
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tracker List -->
    <div class="card">
      <div class="card-body">
        <div v-if="store.loading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="store.trackers.length === 0" class="text-center py-4 text-muted">
          暂无 Tracker
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th @click="handleSort('name')" style="cursor: pointer;" class="user-select-none">名称 <i :class="getSortIcon('name')"></i></th>
                <th @click="handleSort('domain')" style="cursor: pointer;" class="user-select-none">域名 <i :class="getSortIcon('domain')"></i></th>
                <th @click="handleSort('ip')" style="cursor: pointer;" class="user-select-none">当前 IP <i :class="getSortIcon('ip')"></i></th>
                <th @click="handleSort('enable')" style="cursor: pointer;" class="text-center user-select-none">状态 <i :class="getSortIcon('enable')"></i></th>
                <th class="text-center" style="white-space: nowrap;">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tracker in sortedTrackers" :key="tracker.domain">
                <td>{{ tracker.name }}</td>
                <td>{{ tracker.domain }}</td>
                <td>{{ tracker.ip || '未设置' }}</td>
                <td class="text-center">
                  <label class="switch">
                      <input type="checkbox" :checked="tracker.enable" @change="toggleTracker(tracker)">
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
                <td class="text-center" style="white-space: nowrap;">
                  <button class="btn-pill btn-pill-success btn-sm me-2" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;" @click="addToWhitelist(tracker)">
                    <i class="bi bi-shield-plus"></i> 加入白名单
                  </button>
                  <button class="btn-pill btn-pill-danger btn-sm" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;" @click="confirmDelete(tracker)">
                    <i class="bi bi-trash"></i> 删除
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <div v-if="showAddModal" class="modal fade show d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">添加 Tracker</h5>
            <button type="button" class="btn-close" @click="showAddModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="handleAddTracker">
              <div class="mb-3">
                <label class="form-label">名称 <span class="text-danger">*</span></label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-tag"></i></span>
                  <input type="text" class="form-control" v-model="newTracker.name" required>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">域名 <span class="text-danger">*</span></label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-globe"></i></span>
                  <input type="text" class="form-control" v-model="newTracker.domain" required>
                </div>
              </div>
              <div class="form-check mb-3">
                <input class="form-check-input" type="checkbox" v-model="newTracker.enable">
                <label class="form-check-label">启用</label>
              </div>
              <div class="form-check mb-3">
                <input class="form-check-input" type="checkbox" v-model="forceCloudflare">
                <label class="form-check-label">标记为Cloudflare(加入白名单)</label>
              </div>
              <div class="text-end">
                <button type="button" class="btn btn-secondary me-2" @click="showAddModal = false">取消</button>
                <button type="submit" class="btn btn-primary" :disabled="adding">
                  <span v-if="adding" class="spinner-border spinner-border-sm me-1"></span>
                  添加
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Batch Add Modal -->
    <div v-if="showBatchModal" class="modal fade show d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">批量添加PT站点</h5>
            <button type="button" class="btn-close" @click="showBatchModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              批量添加的域名将使用当前优选的Cloudflare IP，如果没有优选结果，将使用默认IP：104.16.91.215
            </div>
            <div class="mb-3">
              <label class="form-label">域名列表 (每行一个)</label>
              <div class="input-group">
                <span class="input-group-text"><i class="bi bi-list-ul"></i></span>
                <textarea class="form-control" rows="10" v-model="batchDomains" placeholder="tracker.example.com"></textarea>
              </div>
            </div>
            <div class="text-end">
              <button type="button" class="btn btn-secondary me-2" @click="showBatchModal = false">取消</button>
              <button type="button" class="btn btn-primary" @click="handleBatchAdd" :disabled="batchAdding">
                <span v-if="batchAdding" class="spinner-border spinner-border-sm me-1"></span>
                批量添加
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Cloudflare Whitelist Modal -->
    <div v-if="showWhitelistModal" class="modal fade show d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Cloudflare 白名单管理</h5>
            <button type="button" class="btn-close" @click="showWhitelistModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              在此列表中的域名将被视为 Cloudflare 域名，并使用优选 IP。
            </div>
            
            <div class="input-group mb-3">
              <span class="input-group-text"><i class="bi bi-globe"></i></span>
              <input type="text" class="form-control" v-model="newWhitelistDomain" placeholder="输入域名 (例如: example.com)" @keyup.enter="handleAddWhitelistDomain">
              <button class="btn btn-primary" @click="handleAddWhitelistDomain" :disabled="addingWhitelist">
                <span v-if="addingWhitelist" class="spinner-border spinner-border-sm"></span>
                <span v-else>添加</span>
              </button>
            </div>

            <div v-if="loadingWhitelist" class="text-center py-3">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="whitelistDomains.length === 0" class="text-center py-3 text-muted">
              暂无白名单域名
            </div>
            <ul v-else class="list-group">
              <li v-for="domain in whitelistDomains" :key="domain" class="list-group-item d-flex justify-content-between align-items-center">
                {{ domain }}
                <button class="btn btn-sm btn-outline-danger" @click="handleDeleteWhitelistDomain(domain)">
                  <i class="bi bi-trash"></i>
                </button>
              </li>
            </ul>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showWhitelistModal = false">关闭</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue';
import { useTrackerStore, type Tracker } from '../../stores/trackers';
import { useMobile } from '../../composables/useMobile';
import { useToast } from 'vue-toastification';
import { useConfirm } from '../../composables/useConfirm';

const store = useTrackerStore();
const { isMobile } = useMobile();
const toast = useToast();
const { confirm } = useConfirm();
const showAddModal = ref(false);
const showBatchModal = ref(false);
const adding = ref(false);
const batchAdding = ref(false);
const batchIpUpdating = ref(false);
const optimizing = ref(false);
const clearing = ref(false);
const showWhitelistModal = ref(false);
const whitelistDomains = ref<string[]>([]);
const newWhitelistDomain = ref('');
const loadingWhitelist = ref(false);
const addingWhitelist = ref(false);
const forceCloudflare = ref(false);

const sortColumn = ref<keyof Tracker | null>(null);
const sortDirection = ref<'asc' | 'desc'>('asc');

const handleSort = (column: keyof Tracker) => {
  if (sortColumn.value === column) {
    // 已经在此列排序，切换方向或取消排序
    const defaultDir = column === 'enable' ? 'desc' : 'asc';
    const altDir = column === 'enable' ? 'asc' : 'desc';

    if (sortDirection.value === defaultDir) {
      sortDirection.value = altDir;
    } else {
      sortColumn.value = null; // 第三次点击回到默认不排序
      sortDirection.value = 'asc';
    }
  } else {
    // 第一次点击该列，'enable' 默认为倒序（开启的在上），其余为正序
    sortColumn.value = column;
    sortDirection.value = column === 'enable' ? 'desc' : 'asc';
  }
};

const getSortIcon = (column: keyof Tracker) => {
  if (sortColumn.value !== column) return 'bi bi-arrow-down-up text-muted ms-1 opacity-25';
  return sortDirection.value === 'asc' ? 'bi bi-sort-down text-primary ms-1' : 'bi bi-sort-up text-primary ms-1';
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


const newTracker = reactive<Tracker>({
  name: '',
  domain: '',
  enable: true,
  ip: ''
});

const batchDomains = ref('');
const batchIp = ref('');

onMounted(async () => {
  await store.fetchConfig();

});

const isValidIpv4 = computed(() => {
  if (!batchIp.value) return false;
  const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  return ipv4Regex.test(batchIp.value.trim());
});



const toggleTracker = async (tracker: Tracker) => {
  try {
    await store.updateTracker(tracker.domain, { enable: !tracker.enable });
  } catch (e: any) {
    const detail = e.response?.data?.detail || e.message || '未知错误';
    toast.error(`更新失败: ${detail}`);
    // Revert logic handled in store or need to force refresh
    store.fetchConfig();
  }
};

const addToWhitelist = async (tracker: Tracker) => {
  if (!await confirm(`确定要将 ${tracker.domain} 加入 Cloudflare 白名单吗？`, '加入白名单')) return;
  try {
    await store.addCloudflareDomain(tracker.domain);
    toast.success('添加成功');
  } catch (e) {
    toast.error('添加失败');
  }
};

const confirmDelete = async (tracker: Tracker) => {
  if (await confirm(`确定要删除 ${tracker.domain} 吗？`, '删除确认')) {
    try {
      await store.deleteTracker(tracker.domain);
      toast.success('删除成功');
    } catch (e: any) {
      const detail = e.response?.data?.detail || e.message || '未知错误';
      toast.error(`删除失败: ${detail}`);
    }
  }
};

const handleAddTracker = async () => {
  adding.value = true;
  try {
    await store.addTracker({ ...newTracker }, forceCloudflare.value);
    showAddModal.value = false;
    newTracker.name = '';
    newTracker.domain = '';
    newTracker.enable = true;
    forceCloudflare.value = false;
    toast.success('添加成功');
  } catch (e: any) {
    const detail = e.response?.data?.detail || e.message || '未知错误';
    toast.error(`添加失败: ${detail}`);
  } finally {
    adding.value = false;
  }
};

const handleBatchAdd = async () => {
  if (!batchDomains.value.trim()) return;
  batchAdding.value = true;
  try {
    const domains = batchDomains.value.split('\n').map(d => d.trim()).filter(d => d);
    const res = await store.batchAddTrackers(domains);
    showBatchModal.value = false;
    batchDomains.value = '';
    toast.success(res?.message || '批量添加成功');
  } catch (e: any) {
    const detail = e.response?.data?.detail || e.message || '未知错误';
    toast.error(`批量添加失败: ${detail}`);
  } finally {
    batchAdding.value = false;
  }
};

const handleBatchUpdateIp = async () => {
  if (!batchIp.value.trim()) return;
  if (!await confirm(`确定要将所有 Tracker 的 IP 修改为 ${batchIp.value} 吗？`, '批量修改IP')) return;
  
  batchIpUpdating.value = true;
  try {
    await store.updateAllTrackersIp(batchIp.value.trim());
    batchIp.value = '';
    toast.success('批量修改成功');
  } catch (e: any) {
    const detail = e.response?.data?.detail || e.message || '未知错误';
    toast.error(`批量修改失败: ${detail}`);
  } finally {
    batchIpUpdating.value = false;
  }
};

const handleRunIpOptimization = async () => {
  optimizing.value = true;
  try {
    await store.runIpOptimization();
    toast.success('IP优选任务已启动，请留意通知或日志');
  } catch (e: any) {
    const detail = e.response?.data?.detail || e.message || '未知错误';
    toast.error(`启动IP优选失败: ${detail}`);
  } finally {
    optimizing.value = false;
  }
};

const handleClearAllTrackers = async () => {
  if (!await confirm('确定要清空所有 Tracker 吗？此操作不可恢复！', '清空确认')) return;
  clearing.value = true;
  try {
    await store.clearAllTrackers();
    toast.success('所有 Tracker 已清空');
  } catch (e: any) {
    const detail = e.response?.data?.detail || e.message || '未知错误';
    toast.error(`清空失败: ${detail}`);
  } finally {
    clearing.value = false;
  }
};

const openWhitelistModal = async () => {
  showWhitelistModal.value = true;
  loadingWhitelist.value = true;
  try {
    whitelistDomains.value = await store.fetchCloudflareDomains();
  } catch (e: any) {
    const detail = e.response?.data?.detail || e.message || '未知错误';
    toast.error(`获取白名单失败: ${detail}`);
  } finally {
    loadingWhitelist.value = false;
  }
};

const handleAddWhitelistDomain = async () => {
  if (!newWhitelistDomain.value.trim()) return;
  addingWhitelist.value = true;
  try {
    await store.addCloudflareDomain(newWhitelistDomain.value.trim());
    newWhitelistDomain.value = '';
    whitelistDomains.value = await store.fetchCloudflareDomains();
    toast.success('添加成功');
  } catch (e: any) {
    const detail = e.response?.data?.detail || e.message || '未知错误';
    toast.error(`添加失败: ${detail}`);
  } finally {
    addingWhitelist.value = false;
  }
};

const handleDeleteWhitelistDomain = async (domain: string) => {
  if (!await confirm(`确定要移除 ${domain} 吗？`, '移除白名单')) return;
  try {
    await store.deleteCloudflareDomain(domain);
    whitelistDomains.value = await store.fetchCloudflareDomains();
    toast.success('删除成功');
  } catch (e: any) {
    const detail = e.response?.data?.detail || e.message || '未知错误';
    toast.error(`删除白名单域失败: ${detail}`);
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
