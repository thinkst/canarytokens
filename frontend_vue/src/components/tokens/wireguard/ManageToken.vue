<template>
  <TokenDisplay :token-data="tokenData" />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';
import TokenDisplay from './TokenDisplay.vue';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenData = ref({
  qr_code: props.tokenBackendResponse?.wg_qr_code,
  wg_conf: props.tokenBackendResponse?.wg_conf,
});
</script>
