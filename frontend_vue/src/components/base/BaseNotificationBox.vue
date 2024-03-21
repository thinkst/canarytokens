<template>
  <div
    class="flex flex-row items-center justify-between flex-grow w-full px-24 py-16 rounded-xl"
    :class="boxClasses"
  >
    <div class="flex flex-row items-center gap-24">
      <AlertShield
        v-if="variant !== 'info'"
        class="w-[4em]"
        :class="iconClass"
      />
      <font-awesome-icon
        v-else
        class="w-[4em]"
        :class="iconClass"
      />
      <p>{{ message }}</p>
    </div>
    <BaseButton
      v-if="link"
      class="whitespace-nowrap"
      :variant="props.variant"
      >{{ textLink }}</BaseButton
    >
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import AlertShield from '../icons/AlertShield.vue';

const props = defineProps<{
  variant: 'info' | 'warning' | 'danger';
  message: string;
  link?: string;
  textLink?: string;
}>();

const boxClasses = computed(() => {
  switch (props.variant) {
    case 'danger':
      return 'bg-red-100 text-red-500 bg-red-100';
    case 'warning':
      return 'text-yellow-700 bg-yellow-300';
    case 'info':
      return 'text-blue-700 bg-blue-300';
    default:
      return 'text-blue-700 bg-blue-300';
  }
});

const iconClass = computed(() => {
  switch (props.variant) {
    case 'warning':
      return 'fill-yellow';
    case 'danger':
      return 'fill-red';
    case 'info':
      return 'fill-blue';
    default:
      return 'fill-blue';
  }
});
</script>
