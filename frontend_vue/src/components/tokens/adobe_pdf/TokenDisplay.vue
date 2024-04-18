<template>
  <div class="flex justify-center">
    <base-button
      class="mt-16"
      @click="handleDownloadPDFDocument"
      >Download your PDF file</base-button
    >
  </div>
</template>
<script setup lang="ts">
import { downloadAsset } from '@/api/main';

type PDFDataType = {
  auth: string;
  token: string;
};
const props = defineProps<{
  tokenData: PDFDataType;
}>();

async function handleDownloadPDFDocument() {
  const params = {
    fmt: 'pdf',
    auth: props.tokenData?.auth,
    token: props.tokenData?.token,
  };
  try {
    const res = await downloadAsset(params);
    window.location.href = res.request.responseURL;
  } catch (err) {
    console.log(err, 'File download failed');
  } finally {
    console.log('Donwload ready');
  }
}
</script>
