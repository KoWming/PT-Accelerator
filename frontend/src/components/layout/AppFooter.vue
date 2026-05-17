<script setup lang="ts">
defineOptions({
  name: 'AppFooter',
});

defineProps<{
  appVersion: string;
  hitokotoText: string;
}>();

defineEmits<{
  focusVersion: [];
}>();
</script>

<template>
  <footer class="text-center py-3 text-muted small">
    <p class="mb-0">
      PT-Accelerator &copy; {{ new Date().getFullYear() }}
      <span
        class="version-pill"
        tabindex="0"
        @mouseenter="$emit('focusVersion')"
        @focus="$emit('focusVersion')"
      >
        {{ appVersion }}
        <span class="easter-egg-tooltip">
          {{ hitokotoText }}
          <i class="star-1">✦</i>
          <i class="star-2">★</i>
          <i class="star-3">✦</i>
          <i class="star-4">★</i>
        </span>
      </span>
      <a href="https://github.com/KoWming/PT-Accelerator" target="_blank" rel="noopener noreferrer" class="github-link">
        <i class="bx bxl-github"></i>
        <span>GitHub</span>
      </a>
    </p>
  </footer>
</template>
