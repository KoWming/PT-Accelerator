<template>
  <div class="cron-input-wrapper position-relative">
    <div class="input-group" @click="$emit('edit')">
      <span class="input-group-text"><i class="bi bi-clock"></i></span>
      <input 
        type="text" 
        class="form-control font-monospace cursor-pointer pe-5" 
        :value="modelValue" 
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        placeholder="点击编辑 CRON 表达式"
      >
    </div>
    <span 
      v-if="modelValue"
      class="clear-btn position-absolute d-flex align-items-center justify-content-center text-muted" 
      @click.stop="$emit('update:modelValue', '')"
      title="清空"
    >
      <i class="bi bi-x-lg" style="font-size: 0.75rem;"></i>
    </span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string;
}>();

defineEmits<{
  (e: 'edit'): void;
  (e: 'update:modelValue', value: string): void;
}>();
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
.clear-btn {
  right: 10px;
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
  background-color: rgba(var(--text-main), 0.1);
  color: var(--text-main) !important;
}
</style>
