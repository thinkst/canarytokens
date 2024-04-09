<template>
  <TokenDisplay :token-png="props.tokenBackendResponse.qr_code" />
</template>

<script lang="ts" setup>
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();
</script>
