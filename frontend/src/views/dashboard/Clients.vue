<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">下载器管理</h2>
      <Teleport to="#mobile-header-actions" :disabled="!isMobile">
        <div v-if="isMobile || true">
          <button class="btn-pill btn-pill-success me-2" @click="handleImportTrackers" :disabled="importing">
            <span v-if="importing" class="spinner-border spinner-border-sm" :class="{ 'me-1': !isMobile }"></span>
            <i v-else class="bi bi-cloud-download" :class="{ 'me-1': !isMobile }"></i>
            <span v-if="!isMobile">导入Tracker</span>
          </button>
          <button class="btn-pill btn-pill-primary" @click="openAddModal">
            <i class="bi bi-plus-circle" :class="{ 'me-1': !isMobile }"></i>
            <span v-if="!isMobile">添加下载器</span>
          </button>
        </div>
      </Teleport>
    </div>

    <!-- Client List -->
    <div v-if="store.loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="store.clients.length === 0" class="card">
      <div class="card-body text-center py-5">
        <i class="bi bi-info-circle fs-1 text-muted"></i>
        <h5 class="mt-3">暂无下载器配置</h5>
        <p class="text-muted">点击"添加下载器"按钮开始配置您的下载器客户端</p>
      </div>
    </div>
    <div v-else class="row">
      <div class="col-md-6 col-lg-4 mb-4" v-for="client in store.clients" :key="client.id">
        <div class="card h-100">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span class="fw-bold">{{ client.name }}</span>
            <div class="d-flex align-items-center gap-2">
              <span class="badge" :class="getTypeBadgeClass(client.type)">{{ getTypeNameShort(client.type) }}</span>
              <span class="badge" :class="client.enable ? 'badge-enabled' : 'badge-disabled'">
                {{ client.enable ? '已启用' : '已禁用' }}
              </span>
            </div>
          </div>
          <div class="card-body">
            <p class="mb-1"><small class="text-muted">地址:</small> {{ client.use_https ? 'https' : 'http' }}://{{ client.host }}:{{ client.port }}</p>
            <p class="mb-1"><small class="text-muted">用户:</small> {{ client.username || '(未设置)' }}</p>
            <p v-if="client.type === 'transmission'" class="mb-1"><small class="text-muted">RPC:</small> {{ client.path }}</p>
          </div>
          <div class="card-footer bg-transparent border-top-0 d-flex justify-content-end gap-2 pb-3">
             <button class="btn-pill btn-pill-success" @click="testConnection(client.id)" :disabled="testing === client.id">
               <span v-if="testing === client.id" class="spinner-border spinner-border-sm"></span>
               <span v-else><i class="bi bi-check-circle me-1"></i>测试</span>
             </button>
             <button class="btn-pill btn-pill-primary" @click="openEditModal(client)">
               <i class="bi bi-pencil me-1"></i>编辑
             </button>
             <button class="btn-pill btn-pill-danger" @click="confirmDelete(client)">
               <i class="bi bi-trash me-1"></i>删除
             </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showModal" class="modal fade show d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEdit ? '编辑' : '添加' }}下载器</h5>
            <button type="button" class="btn-close" @click="showModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="handleSaveClient">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">客户端名称 <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-tag"></i></span>
                    <input type="text" class="form-control" v-model="form.name" required>
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">类型 <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-hdd-network"></i></span>
                    <select class="form-select" v-model="form.type" required :disabled="isEdit" @change="onTypeChange">
                      <option value="">选择类型</option>
                      <option v-for="type in store.supportedTypes" :key="type.type" :value="type.type">
                        {{ type.name }}
                      </option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">主机地址 <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-pc-display"></i></span>
                    <input type="text" class="form-control" v-model="form.host" required>
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">端口 <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-123"></i></span>
                    <input type="number" class="form-control" v-model="form.port" required>
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">用户名</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-person"></i></span>
                    <input type="text" class="form-control" v-model="form.username">
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">密码</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-key"></i></span>
                    <input type="password" class="form-control" v-model="form.password">
                  </div>
                </div>
                <div class="col-md-6 mb-3" v-if="form.type === 'transmission'">
                  <label class="form-label">RPC 路径</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-folder2-open"></i></span>
                    <input type="text" class="form-control" v-model="form.path">
                  </div>
                </div>
                <div class="col-md-6 mb-3 pt-4">
                  <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" v-model="form.use_https">
                    <label class="form-check-label">使用 HTTPS</label>
                  </div>
                  <div class="form-check form-switch mt-2">
                    <input class="form-check-input" type="checkbox" v-model="form.enable">
                    <label class="form-check-label">启用客户端</label>
                  </div>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-info" @click="testConfig" :disabled="testingConfig">
              <span v-if="testingConfig" class="spinner-border spinner-border-sm me-1"></span>
              测试连接
            </button>
            <button type="button" class="btn btn-secondary" @click="showModal = false">取消</button>
            <button type="button" class="btn btn-primary" @click="handleSaveClient" :disabled="saving">
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
import { ref, onMounted, reactive } from 'vue';
import { useClientStore, type TorrentClient } from '../../stores/clients';
import { useMobile } from '../../composables/useMobile';
import { useToast } from 'vue-toastification';
import { useConfirm } from '../../composables/useConfirm';

const store = useClientStore();
const { isMobile } = useMobile();
const toast = useToast();
const { confirm } = useConfirm();
const showModal = ref(false);
const isEdit = ref(false);
const importing = ref(false);
const testing = ref<string | null>(null);
const testingConfig = ref(false);
const saving = ref(false);

const form = reactive<TorrentClient>({
  id: '',
  name: '',
  type: '',
  host: 'localhost',
  port: 8080,
  username: '',
  password: '',
  use_https: false,
  path: '/transmission/rpc',
  enable: true
});

onMounted(async () => {
  await store.fetchSupportedTypes();
  await store.fetchClients();
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
  Object.assign(form, {
    id: '',
    name: '',
    type: '',
    host: 'localhost',
    port: 0,
    username: '',
    password: '',
    use_https: false,
    path: '/transmission/rpc',
    enable: true
  });
  showModal.value = true;
};

const openEditModal = (client: TorrentClient) => {
  isEdit.value = true;
  Object.assign(form, client);
  showModal.value = true;
};

const onTypeChange = () => {
  const t = store.supportedTypes.find(t => t.type === form.type);
  if (t) {
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
    const clients = [...store.clients];
    if (isEdit.value) {
      const index = clients.findIndex(c => c.id === form.id);
      if (index !== -1) {
        clients[index] = { ...form };
      }
    } else {
      const newId = `${form.type}_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
      clients.push({ ...form, id: newId });
    }
    
    await store.saveClients(clients);
    showModal.value = false;
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
    const res = await store.testConnectionConfig({ ...form });
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

const handleImportTrackers = async () => {
  importing.value = true;
  try {
    const res = await store.importTrackers();
    let msg = res.message;
    if (res.client_summary) {
        msg += `\n详情：${res.client_summary}`;
    }
    toast.success(msg);
  } catch (e) {
    toast.error('导入失败');
  } finally {
    importing.value = false;
  }
};
</script>
