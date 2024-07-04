<template>
  <div class="flex justify-center">
    <base-button
      class="mt-16"
      @click="handleDownloadExcelDocument"
      >Download your MS Excel file</base-button
    >
  </div>
</template>
<script setup lang="ts">
import { downloadAsset } from '@/api/main';

type MSExcelDataType = {
  auth: string;
  token: string;
};
const props = defineProps<{
  tokenData: MSExcelDataType;
}>();

async function handleDownloadExcelDocument() {
  const params = {
    fmt: 'msexcel',
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
