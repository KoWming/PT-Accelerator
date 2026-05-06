<template>
  <section v-if="cards.length" :class="gridClass">
    <article v-for="card in cards" :key="card.label" :class="cardClass">
      <span class="settings-field-label">{{ card.label }}</span>
      <strong>{{ card.value }}</strong>
      <p>{{ card.description }}</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import type { PageOverviewCard } from '@/types/settings';

withDefaults(defineProps<{
  cards: PageOverviewCard[];
  gridClass?: string;
  cardClass?: string;
}>(), {
  gridClass: 'settings-section-overview-grid',
  cardClass: 'settings-section-overview-card',
});
</script>
