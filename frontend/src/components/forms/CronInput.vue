<template>
  <div ref="wrapperRef" class="cron-input-wrapper position-relative">
    <div class="input-group cron-input-group" @click="handleWrapperClick">
      <span class="input-group-text"><i class="bx bx-time-five"></i></span>
      <input
        ref="inputRef"
        type="text"
        class="form-control font-monospace pe-5"
        :value="modelValue"
        @focus="openDropdown"
        @input="handleInput"
        placeholder="点击选择或输入 CRON 表达式"
      >
      <button
        type="button"
        class="cron-trigger-btn"
        :class="{ 'is-open': dropdownOpen }"
        @click.stop="toggleDropdown"
        title="展开常用表达式"
      >
        <i class="bx bx-chevron-down"></i>
      </button>
    </div>

    <span
      v-if="modelValue"
      class="clear-btn position-absolute d-flex align-items-center justify-content-center text-muted"
      @click.stop="clearValue"
      title="清空"
    >
      <i class="bx bx-x" style="font-size: 0.9rem;"></i>
    </span>

    <transition name="cron-dropdown">
      <div v-if="dropdownOpen" class="cron-dropdown-panel">
        <div class="cron-dropdown-head">
          <span>常用表达式</span>
          <small>选择后自动填入输入框，亦可自定义输入。</small>
        </div>

        <div class="cron-dropdown-scroll">
          <button
            v-for="option in cronOptions"
            :key="option.value"
            type="button"
            class="cron-option"
            :class="{ 'is-active': modelValue === option.value }"
            @click="selectOption(option.value)"
          >
            <div class="cron-option-main">
              <strong>{{ option.label }}</strong>
              <span>{{ option.description }}</span>
            </div>
            <code>{{ option.value }}</code>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';

defineProps<{
  modelValue: string;
}>();

const emit = defineEmits<{
  (e: 'edit'): void;
  (e: 'update:modelValue', value: string): void;
}>();

const wrapperRef = ref<HTMLElement | null>(null);
const inputRef = ref<HTMLInputElement | null>(null);
const dropdownOpen = ref(false);

const cronOptions = [
  { label: '每天 00:00', description: '每天 00:00 执行', value: '0 0 * * *' },
  { label: '每 6 小时', description: '每6小时执行一次', value: '0 */6 * * *' },
  { label: '每周日 00:00', description: '每周日 00:00 执行', value: '0 0 * * 0' },
  { label: '白天整点', description: '每天9-18点整点执行', value: '0 9-18 * * *' },
  { label: '每 30 分钟', description: '每30分钟执行一次', value: '*/30 * * * *' },
  { label: '每月 1 日凌晨', description: '每月1日 02:00 执行', value: '0 2 1 * *' }
] as const;

const openDropdown = () => {
  dropdownOpen.value = true;
  emit('edit');
};

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value;
  if (dropdownOpen.value) {
    inputRef.value?.focus();
    emit('edit');
  }
};

const handleWrapperClick = () => {
  inputRef.value?.focus();
  openDropdown();
};

const handleInput = (event: Event) => {
  emit('update:modelValue', (event.target as HTMLInputElement).value);
  dropdownOpen.value = true;
};

const selectOption = (value: string) => {
  emit('update:modelValue', value);
  dropdownOpen.value = false;
  inputRef.value?.focus();
};

const clearValue = () => {
  emit('update:modelValue', '');
  inputRef.value?.focus();
  dropdownOpen.value = true;
};

const handleClickOutside = (event: MouseEvent) => {
  if (!wrapperRef.value?.contains(event.target as Node)) {
    dropdownOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside);
});
</script>

<style scoped>
.cron-input-group {
  position: relative;
}

.cron-input-group .form-control {
  border-top-left-radius: 0 !important;
  border-bottom-left-radius: 0 !important;
  border-top-right-radius: 0.9rem !important;
  border-bottom-right-radius: 0.9rem !important;
}

.cron-input-group .input-group-text {
  border-top-left-radius: 0.9rem !important;
  border-bottom-left-radius: 0.9rem !important;
  border-top-right-radius: 0 !important;
  border-bottom-right-radius: 0 !important;
}

.clear-btn {
  right: 2.15rem;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  z-index: 10;
  transition: background-color 0.2s;
  background-color: transparent; /* Ensure default is transparent */
}
.clear-btn:hover {
  background-color: color-mix(in srgb, var(--bg-surface-alt) 84%, var(--primary-color));
  color: var(--text-main) !important;
}

.cron-trigger-btn {
  position: absolute;
  top: 50%;
  right: 0.35rem;
  transform: translateY(-50%);
  width: 1.75rem;
  height: 1.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 0.55rem;
  background: transparent;
  color: var(--text-muted);
  transition: background-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
  z-index: 11;
}

.cron-trigger-btn:hover,
.cron-trigger-btn.is-open {
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
}

.cron-trigger-btn.is-open i {
  transform: rotate(180deg);
}

.cron-trigger-btn i {
  transition: transform 0.2s ease;
}

.cron-dropdown-panel {
  position: absolute;
  top: calc(100% + 0.55rem);
  left: 50%;
  transform: translateX(-50%);
  width: min(24rem, calc(100vw - 2rem));
  z-index: 30;
  padding: 0.58rem;
  border-radius: 1rem;
  border: 1px solid rgba(var(--primary-rgb), 0.14);
  background: color-mix(in srgb, var(--bg-surface) 94%, white 6%);
  box-shadow: 0 1rem 2rem rgba(15, 23, 42, 0.12);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.cron-dropdown-scroll {
  max-height: 6.9rem;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.cron-dropdown-scroll::-webkit-scrollbar {
  width: 0;
  height: 0;
  display: none;
}

.cron-dropdown-head {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding: 0.1rem 0.12rem 0.45rem;
}

.cron-dropdown-head span {
  font-size: 0.84rem;
  font-weight: 700;
  color: var(--text-heading);
}

.cron-dropdown-head small {
  color: var(--text-muted);
  font-size: 0.74rem;
}

.cron-option {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.85rem;
  padding: 0.52rem 0.68rem;
  border: 1px solid transparent;
  border-radius: 0.85rem;
  background: transparent;
  text-align: left;
  transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}

.cron-option + .cron-option {
  margin-top: 0.22rem;
}

.cron-option:hover,
.cron-option.is-active {
  background: rgba(var(--primary-rgb), 0.08);
  border-color: rgba(var(--primary-rgb), 0.16);
}

.cron-option-main {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.08rem;
}

.cron-option-main strong {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-heading);
  line-height: 1.15;
}

.cron-option-main span {
  font-size: 0.71rem;
  color: var(--text-muted);
  line-height: 1.15;
}

.cron-option code {
  flex-shrink: 0;
  padding: 0.18rem 0.4rem;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.06);
  color: color-mix(in srgb, var(--text-heading) 82%, white 18%);
  font-size: 0.7rem;
  line-height: 1.1;
}

.cron-dropdown-enter-active,
.cron-dropdown-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.cron-dropdown-enter-from,
.cron-dropdown-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-6px);
}

.cron-dropdown-enter-to,
.cron-dropdown-leave-from {
  transform: translateX(-50%) translateY(0);
}

@media (max-width: 767.98px) {
  .cron-dropdown-panel {
    width: min(100%, calc(100vw - 2rem));
  }

  .cron-option {
    align-items: flex-start;
    flex-direction: column;
    gap: 0.4rem;
  }

  .cron-option code {
    width: 100%;
  }
}
</style>
