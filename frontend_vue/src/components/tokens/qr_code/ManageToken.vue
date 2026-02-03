<template>
  <TokenDisplay :token-data="tokenData" />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenData = ref({
  qrcode_png: props.tokenBackendResponse?.qr_code,
  token: props.tokenBackendResponse?.canarydrop?.canarytoken?._value,
  auth: props.tokenBackendResponse.canarydrop?.auth as string,
});
</script>
