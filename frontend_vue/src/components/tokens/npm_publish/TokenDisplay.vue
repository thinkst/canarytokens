<template>
  <base-code-snippet
    lang="bash"
    label="NPM publish canary"
    :code="npmCode"
  />
  <base-button
    class="mt-16"
    @click="handleDownloadWorkspace"
  >
    Download canary workspace
  </base-button>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { downloadAsset } from '@/api/main';

type NPMPublishDataType = {
  auth: string;
  token: string;
  npm_token: string;
  npm_package_name: string;
  npm_package_version: string;
};

const props = defineProps<{
  tokenData: NPMPublishDataType;
}>();

const npmCode = ref(`export NPM_TOKEN=${props.tokenData.npm_token}
# package: ${props.tokenData.npm_package_name}
# version to publish: ${props.tokenData.npm_package_version}`);

async function handleDownloadWorkspace() {
  const params = {
    fmt: 'npm_publish',
    auth: props.tokenData?.auth,
    token: props.tokenData?.token,
  };

  try {
    const res = await downloadAsset(params);
    window.location.href = res.request.responseURL;
  } catch (err) {
    console.log(err, 'File download failed');
  }
}
</script>
