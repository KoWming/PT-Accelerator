<template>
  <div class="page-header">
    <h2 class="page-title">{{ title }}</h2>
    <Teleport v-if="hasActions" to="#mobile-header-actions" :disabled="!isMobile">
      <div class="page-header-actions">
        <slot name="actions" />
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, useSlots } from 'vue';

withDefaults(defineProps<{
  title: string;
  isMobile?: boolean;
}>(), {
  isMobile: false,
});

const slots = useSlots();
const hasActions = computed(() => Boolean(slots.actions));
</script>
