<template>
  <div
    :class="`${spinnerClass} border-4 rounded-full border-l-[transparent] animate-spin aspect-square`"
    :style="{ height: height, width: height }"
  ></div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { PropType } from 'vue';
import type { BaseColorVariantType } from './types';

enum SpinnerVariantEnum {
  PRIMARY = 'primary',
  SECONDARY = 'secondary',
  DANGER = 'danger',
}

const props = defineProps({
  variant: {
    type: String as PropType<BaseColorVariantType>,
    default: 'primary',
  },
  height: {
    type: String,
    default: '2rem',
  },
});

const spinnerClass = computed(() => {
  switch (props.variant) {
    case SpinnerVariantEnum.PRIMARY:
      return `border-green-500`;
    case SpinnerVariantEnum.SECONDARY:
      return 'border-white';
    case SpinnerVariantEnum.DANGER:
      return 'border-red';
    default:
      return 'border-green-500';
  }
});
</script>
