<template>
  <main class="flex items-start justify-center mb-24 main-height header-bg">
    <div
      class="lg:max-w-screen-2xl md:max-w-[80svw] m-24 md:mx-[10svw] bg-white rounded-3xl shadow-lg shadow-grey-200/40 min-h-[50vh] sm:px-40 sm:py-32 p-16 flex-auto"
    >
      <h1
        v-if="route.name !== 'home' && route.name !== 'generate'"
        class="text-grey-800"
      >
        {{ title }}
      </h1>
      <slot></slot>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

const title = computed(() => route.meta.title);
</script>

<style scoped>
.header-bg::after {
  content: '';
  background: linear-gradient(
    360deg,
    #38ff7f -43.49%,
    rgba(56, 127, 127, 0.94) 118%
  );
  position: absolute;
  top: 0;
  left: 0;
  height: 15rem;
  width: 100%;
  z-index: -1;
}

/* calculate the height of the main content */
/* 96px is the height of the header */
/* 24px is the padding of the main content */
/* 155px is the height of the footer */
.main-height {
  min-height: calc(100svh - (96px + 24px + 155px));
}

h1 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  text-align: center;
}
</style>
