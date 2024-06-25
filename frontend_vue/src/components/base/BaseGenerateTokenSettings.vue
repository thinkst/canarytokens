<template>
  <div
    class="relative border flex-1 group flex flex-col px-16 sm:px-24 pt-16 pb-24 bg-white rounded-xl top-[0px] shadow-solid-shadow-grey border-grey-200"
  >
    <h3
      class="flex flex-row gap-8 mb-16 text-sm font-semibold text-left text-grey-400"
    >
      <div class="rounded-full bg-grey-200">
        <img
          :src="getImageUrl(`${icon}`)"
          alt="Settings icon"
          aria-hidden="true"
        />
      </div>
      {{ settingType }} Settings
    </h3>
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import getImageUrl from '@/utils/getImageUrl';

const props = defineProps<{
  settingType: 'Canarytoken' | 'Notifications';
}>();

const icon = computed(() => {
  switch (props.settingType) {
    case 'Canarytoken':
      return 'icons/settings.svg';
    case 'Notifications':
      return 'icons/alert.svg';
    default:
      return 'icons/settings.svg';
  }
});
</script>
