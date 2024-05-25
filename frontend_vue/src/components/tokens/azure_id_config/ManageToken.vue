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
  token: props.tokenBackendResponse?.canarydrop?.canarytoken?._value || '',
  auth: props.tokenBackendResponse.canarydrop?.auth || '',
  client_id: props.tokenBackendResponse.client_id || '',
  css: props.tokenBackendResponse.clonedsite_css || '',
});
</script>
