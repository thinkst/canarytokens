<template>
  <div class="flex justify-center p-8 bg-white rounded-xl">
    <img
      id="qrcode_png"
      :src="tokenData.qr_code"
      alt="qrcode"
    />
  </div>
  <base-code-snippet
    class="my-16"
    lang="bash"
    label="WireGuard VPN config"
    :code="codeSnippet"
    multiline
    custom-height="10rem"
  ></base-code-snippet>
</template>

<script setup lang="ts">
import { ref } from 'vue';

type WireguardConfigDataType = {
  qr_code: string;
  wg_conf: string;
};

const props = defineProps<{
  tokenData: WireguardConfigDataType;
}>();

const codeSnippet = ref(props.tokenData.wg_conf);
</script>
