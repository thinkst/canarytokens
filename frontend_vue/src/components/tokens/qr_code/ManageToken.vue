<template>
  Your Token
  <TokenDisplay :token-png="props.tockenBackendResponse.qr_code" />
</template>

<script lang="ts" setup>
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tockenBackendResponse: ManageTokenBackendType;
}>();
</script>
