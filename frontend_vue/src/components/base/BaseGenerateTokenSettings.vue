<template>
  <div
    class="relative border flex-1 group flex flex-col px-16 sm:px-24 pt-16 pb-24 bg-white rounded-3xl top-[0px] shadow-solid-shadow-grey border-grey-200"
  >
    <h3
      v-if="settingType"
      class="flex flex-row gap-8 mb-16 text-sm font-semibold text-left text-grey-400"
    >
      <font-awesome-icon
        :icon="icon"
        class="pt-4 text-grey-300"
        aria-hidden="true"
      ></font-awesome-icon>
      {{ settingType }} Settings
    </h3>
    <span
      v-else
      class="mb-8"
    ></span>
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  settingType?: 'Additional';
}>();

const icon = computed(() => {
  switch (props.settingType) {
    case 'Additional':
      return 'gear';
    default:
      return 'gear';
  }
});
</script>
