<template>
  <div class="settings-section-shell">
    <article class="workspace-card settings-auth-card">
      <header class="workspace-card-header settings-auth-header">
        <div class="settings-card-heading">
          <div class="settings-card-title-row">
            <h3>安全与认证</h3>
          </div>
          <p>统一管理控制台登录认证、管理员账号与密码更新策略，提升后台访问安全性。</p>
        </div>
      </header>

      <div class="settings-auth-body">
        <form @submit.prevent="$emit('submit')">
          <div class="settings-inline-note" role="alert">
            <i class="bx bx-info-circle"></i>
            <div>
              <span class="settings-inline-note-title">管理员账号和密码在初始化后就是后台的唯一登录凭据。</span>
              <div class="settings-inline-note-text">
                <strong>当前状态:</strong> {{ authInitialized ? '已完成管理员初始化' : '未初始化管理员凭据' }}。{{ authInitialized ? '如需修改密码，请先输入当前密码。' : '请先设置管理员账号和初始密码，保存后将直接作为后续登录凭据。' }}
              </div>
            </div>
          </div>


          <div class="settings-auth-form-grid">

            <section class="settings-form-block settings-form-block-single">
              <div class="settings-block-heading settings-block-heading-inline settings-block-heading-inline-top">
                <h4>管理员账号</h4>
                <div class="settings-status-indicator" :class="authInitialized ? 'settings-status-indicator-active' : 'settings-status-indicator-pending'">
                  <i class="bx" :class="authInitialized ? 'bx-shield-quarter' : 'bx-shield-x'"></i>
                  <span>{{ authInitialized ? '已初始化' : '未初始化' }}</span>
                </div>
              </div>
              <div class="settings-block-heading">
                <p>{{ authInitialized ? '当前登录账号即管理员账号，修改后后续请使用新账号登录。' : '请设置初始化时使用的管理员账号，保存后它会成为后续后台登录账号。' }}</p>
              </div>


              <div class="settings-field-grid settings-field-grid-single">
                <div class="settings-field-card">
                  <label class="form-label settings-form-label">用户名</label>
                  <div class="input-group settings-input-group">
                    <span class="input-group-text"><i class="bx bx-user"></i></span>
                    <input type="text" class="form-control" :value="authForm.username" placeholder="请输入管理员用户名" @input="updateField('username', ($event.target as HTMLInputElement).value)">
                  </div>
                </div>
              </div>
            </section>

            <section class="settings-form-block">
              <div class="settings-block-heading settings-block-heading-inline">
                <h4>{{ authInitialized ? '密码更新' : '初始化密码' }}</h4>
                <span class="settings-mini-note">{{ authInitialized ? '建议定期轮换密码' : '保存后立即生效' }}</span>
              </div>

              <div class="settings-password-divider">
                <span>{{ authInitialized ? '修改密码' : '设置初始密码' }}</span>
              </div>

              <div class="settings-field-grid">
                <div v-if="authInitialized" class="settings-field-card settings-field-card-full">
                  <label class="form-label settings-form-label">当前密码</label>
                  <div class="input-group settings-input-group">
                    <span class="input-group-text"><i class="bx bx-key"></i></span>
                    <input type="password" class="form-control" :value="authForm.current_password" placeholder="请输入当前管理员密码" @input="updateField('current_password', ($event.target as HTMLInputElement).value)">
                  </div>
                  <div class="settings-field-hint">已初始化后修改密码必须先校验当前管理员密码。</div>
                </div>
                <div class="settings-field-card">
                  <label class="form-label settings-form-label">{{ authInitialized ? '新密码' : '初始密码' }}</label>
                  <input type="password" class="form-control settings-standalone-input" :value="authForm.new_password" :placeholder="authInitialized ? '请输入新密码' : '请输入初始化密码'" @input="updateField('new_password', ($event.target as HTMLInputElement).value)">
                  <div class="settings-field-hint">密码要求：至少 8 位，且必须同时包含字母和数字。</div>
                </div>
                <div class="settings-field-card">
                  <label class="form-label settings-form-label">确认{{ authInitialized ? '新密码' : '初始密码' }}</label>
                  <input type="password" class="form-control settings-standalone-input" :value="authForm.confirm_password" :placeholder="authInitialized ? '请再次输入新密码' : '请再次输入初始化密码'" @input="updateField('confirm_password', ($event.target as HTMLInputElement).value)">
                </div>
              </div>
            </section>
          </div>

          <div class="settings-auth-actions settings-cfst-bottom-actions settings-system-bottom-actions">
            <button type="submit" class="settings-save-btn" :disabled="savingAuth">
              <span>
                <span v-if="savingAuth" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bx bx-save"></i>
                保存设置
              </span>
            </button>
          </div>
        </form>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import type { AuthFormState } from '@/types/settings';

defineProps<{
  authInitialized: boolean;
  authForm: AuthFormState;
  savingAuth: boolean;
}>();

const emit = defineEmits<{
  submit: [];
  updateField: [field: keyof AuthFormState, value: string];
}>();

const updateField = (field: keyof AuthFormState, value: string) => {
  emit('updateField', field, value);
};
</script>
