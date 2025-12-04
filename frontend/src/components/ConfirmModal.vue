<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="show" class="modal-backdrop-custom" @click.self="handleCancel">
        <div class="modal-dialog-custom">
          <div class="modal-content-custom">
            <div class="modal-header-custom">
              <h5 class="modal-title-custom">
                <i class="bi bi-exclamation-circle-fill text-danger me-2"></i>
                {{ title }}
              </h5>
              <button type="button" class="btn-close-custom" @click="handleCancel">
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
            <div class="modal-body-custom">
              <p class="mb-0">{{ message }}</p>
            </div>
            <div class="modal-footer-custom">
              <button type="button" class="btn-custom btn-secondary-custom" @click="handleCancel">取消</button>
              <button type="button" class="btn-custom btn-primary-custom" @click="handleConfirm">确认</button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useConfirm } from '../composables/useConfirm';

const { show, title, message, handleConfirm, handleCancel } = useConfirm();
</script>

<style scoped>
.modal-backdrop-custom {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1060;
  backdrop-filter: blur(4px);
}

.modal-dialog-custom {
  width: 90%;
  max-width: 400px;
  animation: modal-slide-in 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-content-custom {
  background: var(--bg-surface);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header-custom {
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--glass-border);
}

.modal-title-custom {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-main);
  display: flex;
  align-items: center;
}

.btn-close-custom {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1rem;
  cursor: pointer;
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 50%;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close-custom:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-main);
}

.modal-body-custom {
  padding: 1.5rem;
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.5;
}

.modal-footer-custom {
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  border-top: 1px solid var(--glass-border);
  background: rgba(0, 0, 0, 0.02);
}

.btn-custom {
  padding: 0.5rem 1.25rem;
  border-radius: 0.75rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.btn-secondary-custom {
  background: transparent;
  border: 1px solid var(--glass-border);
  color: var(--text-muted);
}

.btn-secondary-custom:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-main);
  border-color: var(--text-muted);
}

.btn-primary-custom {
  background: var(--primary-color);
  color: #fff;
  box-shadow: 0 4px 12px rgba(var(--primary-color-rgb), 0.3);
}

.btn-primary-custom:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(var(--primary-color-rgb), 0.4);
  filter: brightness(1.1);
}

/* Animations */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

@keyframes modal-slide-in {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
</style>
