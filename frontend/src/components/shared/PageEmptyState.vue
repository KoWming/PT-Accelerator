<template>
  <div class="workspace-empty" :class="containerClass">
    <div v-if="loading" class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <i v-else class="bx" :class="icon"></i>
    <strong v-if="title">{{ title }}</strong>
    <span>{{ description }}</span>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  description: string;
  title?: string;
  icon?: string;
  loading?: boolean;
  containerClass?: string;
}>(), {
  title: '',
  icon: 'bx-data',
  loading: false,
  containerClass: '',
});
</script>
