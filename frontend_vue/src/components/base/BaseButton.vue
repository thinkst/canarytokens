<template>
  <component
    :is="href ? 'a' : 'button'"
    v-bind="$attrs"
    :class="[
      buttonClass,
      { 'flex flex-row flex-nowrap gap-8 items-center': icon },
      { 'flex-row-reverse': iconPosition === 'right' },
      { 'pointer-events-none': loading },
    ]"
    :href="href"
    :type="!href ? type : null"
  >
    <BaseSpinner
      v-if="loading"
      height="1.5rem"
      :variant="spinnerVariant"
      class="absolute left-0 right-0 ml-auto mr-auto"
    ></BaseSpinner>
    <font-awesome-icon
      v-if="icon"
      :icon="icon"
      aria-hidden="true"
      :class="loading && 'opacity-30'"
    />
    <span :class="loading && 'opacity-30'">
      <slot></slot>
    </span>
  </component>
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
  LIGHT = 'text-light',
  GREY = 'grey',
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
  icon: {
    type: String,
    default: null,
  },
  iconPosition: {
    type: String as PropType<'left' | 'right'>,
    default: 'left',
  },
  href: {
    type: String || null,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  border: {
    type: Boolean,
    default: true,
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
      return `${props.border ? 'with-border' : ''} danger base-button`;
    case ButtonVariantEnum.WARNING:
      return 'text warning base-button';
    case ButtonVariantEnum.INFO:
      return 'text info base-button';
    case ButtonVariantEnum.GREY:
      return 'grey base-button';
    case ButtonVariantEnum.LIGHT:
      return 'text-light base-button';
    default:
      return 'primary base-button';
  }
});

const spinnerVariant = computed(() => {
  switch (props.variant) {
    case ButtonVariantEnum.PRIMARY:
      return ButtonVariantEnum.SECONDARY;
    case ButtonVariantEnum.DANGER:
      return ButtonVariantEnum.SECONDARY;
    default:
      return ButtonVariantEnum.PRIMARY;
  }
});
</script>

<style scoped>
.base-button {
  @apply w-fit relative font-semibold rounded-full px-16 py-8 disabled:pointer-events-none transition duration-100;
}

.base-button[disabled] {
  @apply cursor-not-allowed opacity-70;
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

.text-light {
  @apply hover:text-green-800 focus:text-green-800 text-white;
}

.danger {
  @apply hover:text-red focus:text-red text-red-500;
}

.with-border.danger {
  @apply bg-white hover:bg-red-300 hover:text-white disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none  active:top-[0.15rem] active:text-white focus-visible:outline-0 focus:bg-red-300 focus:text-white focus:border-red focus:outline-0 text-red border shadow-solid-shadow-red border-red;
}

.grey {
  @apply bg-white hover:bg-grey-300 hover:text-white disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none  active:top-[0.15rem] active:text-white focus-visible:outline-0 focus:bg-grey-400 focus:text-white focus:border-grey-500 focus:outline-0 text-grey-500 border shadow-solid-shadow-grey-400 border-grey-400;
}

.warning {
  @apply hover:text-yellow focus:text-yellow text-yellow-700;
}

.info {
  @apply hover:text-blue focus:text-blue text-blue-700;
}
</style>
