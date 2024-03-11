<template>
  <main class="flex items-center justify-center main-height bg-grey-50">
    <div class="flex-grow m-24 md:mx-[10svw] bg-white rounded-lg shadow-lg shadow-grey-200/40 min-h-[50vh] p-24">
      <h1 class="text-grey-800">{{ title }}</h1>
      <slot></slot>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const title = computed(() => route.meta.title);

</script>

<style scoped>
.main-height {
  min-height: calc(100svh - (100px + 100px));
}

h1 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  text-align: center;
}
</style>
