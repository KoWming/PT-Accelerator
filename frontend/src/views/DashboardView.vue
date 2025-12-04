<template>
  <RouterView v-slot="{ Component }">
    <transition name="fade" mode="out-in">
      <component :is="Component" />
    </transition>
  </RouterView>
</template>

<script setup lang="ts">
// This view now acts as a simple wrapper for child routes
</script>
