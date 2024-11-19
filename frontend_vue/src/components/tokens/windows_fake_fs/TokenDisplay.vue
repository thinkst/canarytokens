<template>
  <div class="flex justify-center">
    <base-button
      class="mt-16"
      @click="handleDownloadMSregistryFile"
      >Download your powershell script</base-button
    >
  </div>
</template>

<script setup lang="ts">
import { downloadAsset } from '@/api/main';

type WindowsFakeFSDataType = {
  auth: string;
  token: string;
};

const props = defineProps<{
  tokenData: WindowsFakeFSDataType;
}>();

async function handleDownloadMSregistryFile() {
  const params = {
    fmt: 'windows_fake_fs',
    auth: props.tokenData?.auth,
    token: props.tokenData?.token,
  };
  try {
    const res = await downloadAsset(params);
    window.location.href = res.request.responseURL;
  } catch (err) {
    console.log(err, 'File download failed');
  } finally {
    console.log('Download ready');
  }
}
</script>
