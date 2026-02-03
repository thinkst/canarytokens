<template>
  <div class="flex flex-col items-center">
    <img
      id="qrcode_png"
      :src="tokenData.qrcode_png"
      alt="qrcode"
    />
    <base-button
      class="mt-16"
      :href="href"
      :download="download"
      @click="handleDownloadQRcode()"
      >Download QR code</base-button
    >
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

type QRCodetokenDataType = {
  qrcode_png: string;
  auth: string;
  token: string;
};

const props = defineProps<{
  tokenData: QRCodetokenDataType;
}>();

const href = ref(`${props.tokenData?.token}.png`);
const download = ref(props.tokenData?.qrcode_png);

function handleDownloadQRcode() {
  download.value = `${props.tokenData?.token}.png`;
  href.value = props.tokenData?.qrcode_png;
}
</script>
