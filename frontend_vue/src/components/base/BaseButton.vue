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
import type { ButtonVariantType } from './types';

enum ButtonVariantEnum {
  PRIMARY = 'primary',
  SECONDARY = 'secondary',
  TEXT = 'text',
  DANGER = 'danger',
  WARNING = 'warning',
  INFO = 'info',
}

type buttonType = 'button' | 'submit' | 'reset';

const props = defineProps({
  variant: {
    type: String as PropType<ButtonVariantType>,
    default: 'primary',
  },
  type: {
    type: String as PropType<buttonType>,
    default: 'button',
  },
});

const buttonClass = computed(() => {
  switch (props.variant) {
    case ButtonVariantEnum.PRIMARY:
      return 'primary base-button';
    case ButtonVariantEnum.SECONDARY:
      return 'secondary base-button';
    case ButtonVariantEnum.TEXT:
      return 'text base-button';
    case ButtonVariantEnum.DANGER:
      return 'text danger base-button';
    case ButtonVariantEnum.WARNING:
      return 'text warning base-button';
    case ButtonVariantEnum.INFO:
      return 'text info base-button';
    default:
      return 'primary base-button';
  }
});
</script>

<style scoped>
.base-button {
  @apply w-fit relative font-semibold rounded-full px-16 py-8 disabled:pointer-events-none;
}

.primary {
  @apply bg-green hover:bg-green-300 disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none active:top-[0.15rem] focus-visible:outline-0 focus-visible:border-green-800 focus:bg-green-300 focus:border-green-800 focus:outline-0 text-white border shadow-solid-shadow-green border-green-800;
}

.secondary {
  @apply bg-white hover:bg-green-50 hover:text-green-500 focus:text-green-500 disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none active:top-[0.15rem] focus-visible:outline-0 focus:bg-green-100 focus:border-green-200 focus:outline-0 text-green-600 border shadow-solid-shadow-green-300 border-green-200;
}

.text {
  @apply hover:text-green-500 focus:text-green-800 text-grey-500;
}

.danger {
  @apply hover:text-red focus:text-red text-red-500;
}

.warning {
  @apply hover:text-yellow focus:text-yellow text-yellow-700;
}

.info {
  @apply hover:text-blue focus:text-blue text-blue-700;
}
</style>
