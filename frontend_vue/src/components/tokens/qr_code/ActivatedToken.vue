<template>
  <TokenDisplay :token-data="tokenSnippetData" />
  <base-message-box
    class="mt-24"
    variant="info"
    :message="`When someone scans the QR Code with a reader, it will trigger the URL tied to your token and fire an alert.`"
    text-link="More tips?"
    @click="() => $emit('howToUse')"
  />
  <p class="mt-24 text-sm"></p>
</template>

<script setup lang="ts">
import TokenDisplay from './TokenDisplay.vue';
import { ref } from 'vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

interface QRCodeTokenBackendType extends NewTokenBackendType {
  qrcode_png: string;
}

const props = defineProps<{
  tokenData: QRCodeTokenBackendType;
}>();

defineEmits(['howToUse']);

const tokenSnippetData = ref({
  qrcode_png: props.tokenData.qrcode_png || '',
  token: props.tokenData.token || '',
  auth: props.tokenData.auth_token || '',
});
</script>
