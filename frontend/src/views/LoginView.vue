<template>
  <div class="login-container d-flex align-items-center justify-content-center min-vh-100">
    <div class="login-card card shadow-lg">
      <div class="card-body p-5">
        <div class="text-center mb-4">
          <div class="icon-circle bg-primary bg-opacity-10 text-primary mb-3 mx-auto d-flex align-items-center justify-content-center">
            <i class="bx bxs-bolt-circle fs-2"></i>
          </div>
          <h3 class="fw-bold mb-1">PT-Accelerator</h3>
          <p class="text-muted small mb-0">KoWming Edition</p>
          <p v-if="authStore.authState === 'BROKEN'" class="text-danger small mt-2 mb-0">
            检测到认证配置损坏或疑似被篡改，已禁止在线登录与重新初始化。请在服务器本机执行管理员离线重置。
          </p>
          <p v-else-if="!authStore.initialized" class="text-warning small mt-2 mb-0">
            首次部署初始化：请设置管理员账号与密码。密码至少 8 位，且必须同时包含字母和数字。
          </p>
        </div>

        <div v-if="error" class="alert alert-danger d-flex align-items-center" role="alert">
          <i class="bx bxs-error-circle me-2"></i>
          <div>{{ error }}</div>
        </div>

        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label for="username" class="form-label">{{ authStore.authState === 'BROKEN' ? '管理员账号' : (authStore.initialized ? '用户名' : '管理员账号') }}</label>
            <div class="input-group custom-input-group">
              <span class="input-group-text bg-transparent border-0">
                <i class="bx bx-user text-muted"></i>
              </span>
              <input
                type="text"
                class="form-control border-0 ps-0 bg-transparent"
                id="username"
                v-model="username"
                required
                autofocus
                placeholder="请输入用户名"
              />
            </div>
          </div>
          <div class="mb-4">
            <label for="password" class="form-label">{{ authStore.authState === 'BROKEN' ? '登录已禁用' : (authStore.initialized ? '密码' : '设置密码') }}</label>
            <div class="input-group custom-input-group">
              <span class="input-group-text bg-transparent border-0">
                <i class="bx bx-lock-alt text-muted"></i>
              </span>
              <input
                type="password"
                class="form-control border-0 ps-0 bg-transparent"
                id="password"
                v-model="password"
                required
                minlength="8"
                :disabled="authStore.authState === 'BROKEN'"
                :placeholder="authStore.authState === 'BROKEN' ? '请先在服务器本机执行离线重置' : (authStore.initialized ? '请输入密码' : '请设置初始密码')"
              />
            </div>
            <div v-if="authStore.authState === 'BROKEN'" class="form-text mt-2 text-danger-emphasis">
              在线初始化和登录已被禁用，请在服务器本机执行管理员离线重置后再登录。
            </div>
            <div v-else-if="!authStore.initialized" class="form-text mt-2 text-warning-emphasis">
              密码至少 8 位，且必须同时包含字母和数字。
            </div>
          </div>
          <button type="submit" class="btn btn-primary w-100 py-2 fw-bold" :disabled="loading || authStore.authState === 'BROKEN'">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            {{ authStore.authState === 'BROKEN' ? '请先离线重置' : (loading ? (authStore.initialized ? '登录中...' : '初始化中...') : (authStore.initialized ? '登 录' : '初始化并登录')) }}
          </button>
        </form>
      </div>
      <div class="card-footer bg-transparent border-0 text-center py-3">
        <small class="text-muted">
          &copy; {{ new Date().getFullYear() }} PT-Accelerator-KoWming
        </small>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useAuthRedirect } from '@/composables/useAuthRedirect';
import { getErrorMessage } from '@/utils/error';

const username = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const routeRef = computed(() => route);
const { redirectTarget } = useAuthRedirect(routeRef);

const handleLogin = async () => {
  loading.value = true;
  error.value = '';

  try {
    await authStore.login({
      username: username.value,
      password: password.value
    });
    router.push(redirectTarget.value);
  } catch (e: unknown) {
    error.value = getErrorMessage(e, authStore.initialized ? '用户名或密码错误' : '初始化失败');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  padding: 1.5rem;
  background: transparent;
}

.login-card {
  width: 100%;
  max-width: 400px;
  backdrop-filter: blur(18px);
  background: color-mix(in srgb, var(--bg-surface) 92%, transparent);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-lg);
}

.icon-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--bg-soft-primary);
}

.custom-input-group {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  background: var(--bg-surface-alt);
  overflow: hidden;
  box-shadow: inset 0 1px 2px rgba(67, 89, 113, 0.04);
}

.custom-input-group:focus-within {
  border-color: rgba(var(--primary-rgb), 0.4);
  box-shadow: 0 0 0 0.25rem rgba(var(--primary-rgb), 0.12);
}

.custom-input-group .input-group-text {
  border: none;
  background: transparent;
}

.custom-input-group .form-control {
  border: none;
  background: transparent;
}

.custom-input-group .form-control:focus {
  box-shadow: none;
}

.input-group-text {
  display: flex;
  align-items: center;
}
</style>
