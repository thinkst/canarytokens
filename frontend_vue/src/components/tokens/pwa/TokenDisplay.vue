<template>
  <div
    class="flex flex-col items-center justify-center gap-8 p-16 py-24 m-16 bg-white border border-grey-100 rounded-3xl"
  >
    <div class="p-4 border rounded-2xl border-grey-100">
      <img
        :src="getPwaIconUrl()"
        alt="App icon"
        class="rounded-lg w-[56px] h-[56px]"
      />
    </div>
    <h3
      class="mb-8 text-sm font-semibold leading-tight text-center text-grey-500"
    >
      {{ tokenData.pwa_app_name }}
    </h3>
    <base-button
      class="w-full"
      :href="tokenData.url"
      :download="tokenData.url"
      target="_blank"
      variant="primary"
      >Download Fake App Canarytoken</base-button
    >
  </div>
  <div class="flex justify-center"></div>
</template>

<script setup lang="ts">
import { pwaIconService } from './pwaIconService';

type PWADataType = {
  url: string;
  pwa_icon: string;
  pwa_app_name: string;
};

const props = defineProps<{
  tokenData: PWADataType;
}>();

function getPwaIconUrl() {
  const icon = pwaIconService.find(
    (icon) => icon.value === props.tokenData.pwa_icon
  );
  if (icon) {
    return icon.url;
  } else {
    console.error(`Icon not found for value: ${props.tokenData.pwa_icon}.`);
    return '';
  }
}
</script>
