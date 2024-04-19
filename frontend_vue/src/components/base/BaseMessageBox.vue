<template>
  <div
    class="flex flex-col items-center justify-start flex-grow w-full gap-8 px-24 py-16 rounded-xl md:flex-row"
    :class="boxClasses"
  >
    <div
      class="flex flex-row items-center self-start flex-grow gap-16 md:gap-16 md:self-center"
    >
      <AlertShieldIcon
        v-if="variant !== 'info'"
        class="min-w-[40px]"
        :class="iconClass"
        aria-hidden="true"
      />
      <InfoIcon
        v-else
        class="min-w-[40px]"
        :class="iconClass"
        aria-hidden="true"
      />
      <p
        v-if="message"
        class="text-pretty"
      >
        {{ message }}
      </p>
      <p
        v-else
        class="text-pretty"
      >
        <slot />
      </p>
    </div>
    <BaseButton
      v-if="textLink"
      class="self-end whitespace-nowrap md:self-center"
      :variant="props.variant"
      :href="href"
      @click="$emit('click')"
      >{{ textLink }}</BaseButton
    >
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import AlertShieldIcon from '@/components/icons/AlertShieldIcon.vue';
import InfoIcon from '@/components/icons/InfoIcon.vue';
import type { NotificationBoxVariantType } from './types';

enum VariantEnum {
  DANGER = 'danger',
  WARNING = 'warning',
  INFO = 'info',
}

const props = defineProps<{
  variant: NotificationBoxVariantType;
  message?: string;
  textLink?: string;
  href?: string;
}>();

defineEmits(['click']);

const boxClasses = computed(() => {
  switch (props.variant) {
    case VariantEnum.DANGER:
      return 'bg-red-100 text-red-500 bg-red-100';
    case VariantEnum.WARNING:
      return 'text-yellow-700 bg-yellow-300';
    case VariantEnum.INFO:
      return 'text-blue-700 bg-blue-300';
    default:
      return 'text-blue-700 bg-blue-300';
  }
});

const iconClass = computed(() => {
  switch (props.variant) {
    case VariantEnum.WARNING:
      return 'fill-yellow';
    case VariantEnum.DANGER:
      return 'fill-red';
    case VariantEnum.INFO:
      return 'fill-blue';
    default:
      return 'fill-blue';
  }
});
</script>
