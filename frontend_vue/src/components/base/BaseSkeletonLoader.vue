<template>
  <div :class="[loaderClass, 'relative overflow-hidden bg-grey-100']">
    <div
      class="absolute inset-[0px] shimmer bg-gradient-to-r from-grey-100 via-grey-50 to-transparent"
    ></div>
    <slot />
  </div>
</template>

<script lang="ts">
const LOADER_TYPES = {
  rectangle: 'rectangle',
  circle: 'circle',
  text: 'text',
  header: 'header',
};
</script>

<script setup lang="ts">
import { computed, toRefs } from 'vue';

const props = defineProps({
  type: {
    type: String,
    default: LOADER_TYPES.rectangle,
  },
});

const { type } = toRefs(props);

const LOADER_CSS_CLASSES = {
  [LOADER_TYPES.rectangle]: 'rounded',
  [LOADER_TYPES.circle]: 'rounded-full',
  [LOADER_TYPES.text]: 'h-[16px] rounded',
  [LOADER_TYPES.header]: 'h-[32px] rounded',
};

const loaderClass = computed(() => {
  return `${LOADER_CSS_CLASSES[type.value]}`;
});
</script>

<style scoped>
.shimmer {
  transform: translateX(-100%);
  animation: shimmer 1.4s infinite;
}

@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}
</style>
