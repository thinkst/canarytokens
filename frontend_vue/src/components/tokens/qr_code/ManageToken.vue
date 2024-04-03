<template>
  Never mind the bollocks, here comes the Token
  <TokenDisplay :token-png="props.tokenSnippetData" />
</template>

<script lang="ts" setup>
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenType } from '@/components/types.ts';

const props = defineProps<{
  tockenBackendResponse: ManageTokenType;
  tokenSnippetData: string;
}>();
</script>
