<template>
  <div class="flex justify-center">
    <base-button
      class="mt-16"
      @click="handleDownloadMSregistryFile"
      >Download your MS registry file</base-button
    >
  </div>
  <div v-if="displayInfoBox">
    <base-message-box
      class="mt-24"
      variant="info"
      message="Once installed (with admin permissions) you'll get an alert whenever someone
    (or someone's code) runs your sensitive process."
    />
    <p class="mt-24 text-sm">
      It will automatically provide the command used, computer the command ran on,
      and the user invoking the command.
    </p>
    <p class="mt-16 text-sm"></p>
  </div>
  <base-message-box
    class="mt-24"
    variant="warning"
    message="In order to ensure that the token fires for both 32-bit and 64-bit
    executables, we suggest installing by running the following commands:"
  />
  <BaseCodeSnippet
    class="mt-16"
    lang="bash"
    :code="recommendedReg"
  ></BaseCodeSnippet>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { downloadAsset } from '@/api/main';

type CMDDataType = {
  auth: string;
  token: string;
};

const props = defineProps<{
  tokenData: CMDDataType;
  displayInfoBox: boolean;
}>();

async function handleDownloadMSregistryFile() {
  const params = {
    fmt: 'cmd',
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

const recommendedReg = ref(
  'reg import FILENAME /reg:64  \nreg import FILENAME /reg:32'
);

</script>
