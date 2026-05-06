<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="show" class="modal-backdrop-custom confirm-backdrop" @click.self="handleCancel">
        <div class="modal-dialog-custom confirm-dialog">
          <div class="modal-content-custom confirm-content">
            <div class="modal-header-custom">
              <div class="confirm-title-wrap">
                <span class="confirm-icon" :class="confirmVariantClass">
                  <i :class="confirmIcon"></i>
                </span>
                <div class="confirm-heading">
                  <h5 class="modal-title-custom">{{ title }}</h5>
                  <p>{{ descriptionText }}</p>
                </div>
              </div>
              <button type="button" class="btn-close-custom" @click="handleCancel">
                <i class="bx bx-x"></i>
              </button>
            </div>
            <div class="modal-body-custom confirm-body">
              <span class="confirm-message-label">确认内容</span>
              <p class="mb-0 confirm-message-text">{{ message }}</p>
            </div>
            <div class="modal-footer-custom">
              <button type="button" class="btn-custom btn-secondary-custom confirm-cancel-btn" @click="handleCancel">取消</button>
              <button type="button" class="btn-custom confirm-confirm-btn" :class="confirmActionClass" @click="handleConfirm">确认</button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useConfirm } from '@/composables/useConfirm';

const { show, title, message, handleConfirm, handleCancel } = useConfirm();

const isDangerConfirm = computed(() => {
  const text = `${title.value} ${message.value}`;
  return /删除|移除|清空|危险|不可恢复/.test(text);
});

const confirmVariantClass = computed(() => (isDangerConfirm.value ? 'is-danger' : 'is-primary'));
const confirmActionClass = computed(() => (isDangerConfirm.value ? 'is-danger' : 'is-primary'));
const confirmIcon = computed(() => (isDangerConfirm.value ? 'bx bxs-trash-alt' : 'bx bxs-help-circle'));
const descriptionText = computed(() => (isDangerConfirm.value ? '该操作执行后通常无法撤销，请再次确认。' : '请确认是否继续执行当前操作。'));
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity var(--transition-slow);
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.confirm-backdrop {
  backdrop-filter: blur(10px);
}

.confirm-dialog {
  width: min(92vw, 28rem);
}

.confirm-content {
  border-radius: 1.15rem;
  border-color: rgba(var(--primary-rgb), 0.12);
  box-shadow: 0 1.25rem 3rem rgba(15, 23, 42, 0.22);
  overflow: hidden;
}

.modal-header-custom {
  padding: 1rem 1.25rem;
}

.modal-footer-custom {
  padding: 1rem 1.25rem;
  gap: 0.75rem;
}

.confirm-title-wrap {
  display: flex;
  align-items: flex-start;
  gap: 0.9rem;
  min-width: 0;
}

.confirm-icon {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.85rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  font-size: 1.1rem;
  border: 1px solid transparent;
}

.confirm-icon.is-danger {
  color: var(--danger-color);
  background: color-mix(in srgb, var(--bg-surface-alt) 82%, var(--danger-color));
  border-color: rgba(225, 108, 108, 0.18);
}

.confirm-icon.is-primary {
  color: var(--primary-color);
  background: rgba(var(--primary-rgb), 0.1);
  border-color: rgba(var(--primary-rgb), 0.16);
}

.confirm-heading {
  min-width: 0;
}

.confirm-heading p {
  margin: 0.24rem 0 0;
  color: var(--text-muted);
  font-size: 0.79rem;
  line-height: 1.5;
}

.confirm-body {
  padding-top: 0.4rem;
}

.confirm-message-label {
  display: inline-block;
  margin-bottom: 0.42rem;
  color: var(--text-muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.confirm-message-text {
  color: var(--text-heading);
  font-size: 0.88rem;
  line-height: 1.58;
  word-break: break-word;
}

.btn-close-custom {
  width: 2rem;
  height: 2rem;
}

.btn-custom {
  min-height: 2.125rem;
  padding: 0.375rem 0.875rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
}

.confirm-cancel-btn {
  color: color-mix(in srgb, var(--text-heading) 74%, var(--text-muted));
}

.confirm-confirm-btn.is-danger {
  background: linear-gradient(135deg, rgba(225, 108, 108, 0.96), rgba(225, 108, 108, 0.82));
  border-color: rgba(225, 108, 108, 0.28);
  color: #fff;
  box-shadow: 0 0.75rem 1.5rem rgba(225, 108, 108, 0.18);
}

.confirm-confirm-btn.is-primary {
  background: linear-gradient(135deg, rgba(var(--primary-rgb), 0.98), rgba(var(--primary-rgb), 0.82));
  border-color: rgba(var(--primary-rgb), 0.22);
  color: #fff;
  box-shadow: 0 0.75rem 1.5rem rgba(var(--primary-rgb), 0.18);
}
</style>
