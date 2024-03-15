<template>
  <button
    v-bind="$attrs"
    :class="buttonClass"
    :type="type"
  >
    <slot></slot>
  </button>
</template>

<script setup lang="ts">
import type { PropType } from 'vue';
import { computed } from 'vue';

type variantType = 'primary' | 'secondary' | 'text';
type buttonType = 'button' | 'submit' | 'reset';

const props = defineProps({
  variant: {
    type: String as PropType<variantType>,
    default: 'primary',
  },
  type: {
    type: String as PropType<buttonType>,
    default: 'button',
  },
});

const buttonClass = computed(() => {
  switch (props.variant) {
    case 'primary':
      return 'primary';
    case 'secondary':
      return 'secondary';
    case 'text':
      return 'text';
    default:
      return 'primary';
  }
});
</script>

<style scoped>
.primary {
  @apply w-fit relative bg-green hover:bg-green-300 disabled:pointer-events-none disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none active:top-[0.15rem] focus-visible:outline-0 focus-visible:border-green-800 focus:bg-green-300 focus:border-green-800 focus:outline-0 text-white border shadow-solid-shadow-green border-green-800 font-semibold rounded-full px-16 py-8;
}

.secondary {
  @apply w-fit relative bg-white hover:bg-green-50 hover:text-green-500 focus:text-green-500 disabled:pointer-events-none disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none active:top-[0.15rem] focus-visible:outline-0 focus:bg-green-100 focus:border-green-200 focus:outline-0 text-green-600 border shadow-solid-shadow-green-300 border-green-200 font-semibold rounded-full px-16 py-8;
}

.text {
  @apply w-fit relative font-semibold hover:text-green-500 focus:text-green-800 text-grey-500 rounded-full px-16 py-8;
}
</style>
