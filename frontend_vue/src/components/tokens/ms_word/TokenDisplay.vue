<template>
  <div class="flex flex-col items-center">
    <base-button
      class="mt-16"
      @click="handleDownloadWordDocument"
      >Download your MS Word file</base-button
    >
    <div
      v-if="tokenData.textSnippet"
      class="w-full max-w-3xl mt-24"
    >
      <BaseCodeSnippet
        label="Embedded text snippet"
        :code="tokenData.textSnippet"
        lang="text"
      />
    </div>
  </div>
</template>
<script setup lang="ts">
import { downloadAsset } from '@/api/main';

type MSWordDataType = {
  auth: string;
  token: string;
  textSnippet?: string;
};
const props = defineProps<{
  tokenData: MSWordDataType;
}>();

async function handleDownloadWordDocument() {
  const params = {
    fmt: 'msword',
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
