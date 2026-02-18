<template>
  <base-code-snippet
    lang="javascript"
    label="SVG Image"
    is-single-line
    :code="tokenData.svg"
  ></base-code-snippet>
  <div class="flex justify-center">
    <base-button
      class="mt-16"
      @click="handleDownloadSVG"
      >Download your SVG image</base-button
    >
  </div>
</template>

<script setup lang="ts">
import { downloadAsset } from '@/api/main';

type SVGDataType = {
  auth: string;
  token: string;
  svg: string;
};
const props = defineProps<{
  tokenData: SVGDataType;
}>();

async function handleDownloadSVG() {
  const params = {
    fmt: 'svg',
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
