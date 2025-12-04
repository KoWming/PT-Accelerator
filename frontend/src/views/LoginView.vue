<template>
  <div class="login-container d-flex align-items-center justify-content-center min-vh-100">
    <div class="login-card card shadow-lg">
      <div class="card-body p-5">
        <div class="text-center mb-4">
          <div class="icon-circle bg-primary bg-opacity-10 text-primary mb-3 mx-auto d-flex align-items-center justify-content-center">
            <i class="bi bi-lightning-charge-fill fs-2"></i>
          </div>
          <h3 class="fw-bold mb-1">PT-Accelerator</h3>
          <p class="text-muted small">KoWming Edition</p>
        </div>

        <div v-if="error" class="alert alert-danger d-flex align-items-center" role="alert">
          <i class="bi bi-exclamation-circle-fill me-2"></i>
          <div>{{ error }}</div>
        </div>

        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label for="username" class="form-label">用户名</label>
            <div class="input-group custom-input-group">
              <span class="input-group-text bg-transparent border-0">
                <i class="bi bi-person text-muted"></i>
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
            <label for="password" class="form-label">密码</label>
            <div class="input-group custom-input-group">
              <span class="input-group-text bg-transparent border-0">
                <i class="bi bi-lock text-muted"></i>
              </span>
              <input
                type="password"
                class="form-control border-0 ps-0 bg-transparent"
                id="password"
                v-model="password"
                required
                placeholder="请输入密码"
              />
            </div>
          </div>
          <button type="submit" class="btn btn-primary w-100 py-2 fw-bold" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            {{ loading ? '登录中...' : '登 录' }}
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
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import axios from '../api/axios';

const username = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);
const csrfToken = ref('');

const router = useRouter();
const authStore = useAuthStore();

onMounted(async () => {
  try {
    const response = await axios.get('/csrf');
    csrfToken.value = response.data.token;
  } catch (e) {
    console.error('Failed to fetch CSRF token', e);
  }
});

const handleLogin = async () => {
  loading.value = true;
  error.value = '';

  try {
    const formData = new FormData();
    formData.append('username', username.value);
    formData.append('password', password.value);
    formData.append('csrf_token', csrfToken.value);

    await authStore.login(formData);
    router.push('/');
  } catch (e: any) {
    error.value = '用户名或密码错误';
    // Refresh CSRF token on failure
    try {
        const response = await axios.get('/csrf');
        csrfToken.value = response.data.token;
    } catch (err) {
        console.error('Failed to refresh CSRF token', err);
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  /* Use global background instead of overriding it, or use a transparent one */
  background: transparent;
}

.login-card {
  width: 100%;
  max-width: 400px;
  backdrop-filter: blur(20px);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
}

.icon-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(var(--primary-color), 0.1); /* Use primary color variable */
}

/* Custom Input Group Styles */
.custom-input-group {
  border: 1px solid var(--glass-border);
  border-radius: 0.5rem;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.05);
  overflow: hidden; /* Ensure children don't overflow rounded corners */
}

.custom-input-group:focus-within {
  border-color: var(--primary-color);
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
