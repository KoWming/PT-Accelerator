<template>
  <div class="dashboard-redesign settings-redesign" :class="pageClass">
    <div class="page-header">
      <h2 class="page-title">{{ pageTitle }}</h2>
    </div>

    <section v-if="!hideContextPanel" class="settings-context-panel">
      <div class="settings-context-copy">
        <span v-if="kicker" class="settings-context-kicker">{{ kicker }}</span>
        <div class="settings-context-title-row">
          <h3>{{ contextTitle }}</h3>
          <span class="workspace-pill" :class="loaded ? 'success' : 'danger'">
            <span class="workspace-pill-dot"></span>
            {{ loaded ? loadedText : unloadedText }}
          </span>
        </div>
        <p v-if="description">{{ description }}</p>
      </div>
      <div class="settings-context-actions">
        <button
          type="button"
          class="settings-toolbar-btn settings-toolbar-btn-neutral"
          @click="$emit('refresh')"
          :disabled="refreshing"
        >
          <span v-if="refreshing" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bx bx-refresh me-2"></i>
          {{ refreshText }}
        </button>
      </div>
    </section>

    <SettingsOverviewCards v-if="overviewCards.length" :cards="overviewCards" />

    <SettingsStatusBanner v-if="!hideStatusBanner" :feedback="feedback" />

    <slot />
  </div>
</template>




<script setup lang="ts">
import SettingsOverviewCards from '@/components/settings/shared/SettingsOverviewCards.vue';
import SettingsStatusBanner from '@/components/settings/shared/SettingsStatusBanner.vue';
import type { PageOverviewCard, PageFeedback } from '@/types/settings';

withDefaults(defineProps<{
  pageTitle: string;
  contextTitle: string;
  description: string;
  loaded: boolean;
  refreshing: boolean;
  overviewCards: PageOverviewCard[];
  feedback: PageFeedback;

  pageClass?: string;
  kicker?: string;
  loadedText?: string;
  unloadedText?: string;
  refreshText?: string;
  hideContextPanel?: boolean;
  hideStatusBanner?: boolean;
}>(), {
  pageClass: '',
  kicker: '独立页面',
  loadedText: '已加载',
  unloadedText: '待刷新',
  refreshText: '刷新页面',
  hideContextPanel: false,
  hideStatusBanner: false,
});



defineEmits<{
  (e: 'refresh'): void;
}>();
</script>

