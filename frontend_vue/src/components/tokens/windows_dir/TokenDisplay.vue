<template>
  <div class="flex justify-center">
    <base-button
      class="mt-16"
      @click="handleDownloadWindowsFolderFile"
      >Download your ZIP file</base-button
    >
  </div>
</template>

<script setup lang="ts">
import { downloadAsset } from '@/api/main';

type WindowsFolderDataType = {
  auth: string;
  token: string;
};

const props = defineProps<{
  tokenData: WindowsFolderDataType;
}>();

async function handleDownloadWindowsFolderFile() {
  const params = {
    fmt: 'zip',
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
