<template>
  <div
    class="relative border flex-1 group flex flex-col px-16 sm:px-24 pt-16 pb-24 bg-white rounded-xl top-[0px] shadow-solid-shadow-grey border-grey-200"
  >
    <h3 class="mb-16 text-sm font-semibold text-left text-grey-400">
      {{ settingType }} Settings
    </h3>
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  settingType: 'Canarytoken' | 'Notifications';
}>();
</script>
