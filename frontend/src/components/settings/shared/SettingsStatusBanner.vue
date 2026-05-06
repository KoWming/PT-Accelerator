<template>
  <div
    v-if="feedback?.message"
    class="settings-section-feedback"
    :class="`is-${feedback.status}`"
  >
    <div>
      <strong>{{ feedback.title }}</strong>
      <p>{{ feedback.message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PageFeedback } from '@/types/settings';

defineProps<{
  feedback: PageFeedback;
}>();
</script>
