<template>
  Never mind the bollocks, here comes the Token
  <TokenDisplay :token-data="props.tokenSnippetData" />
</template>

<script lang="ts" setup>
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenType } from '@/components/types.ts';
import { MySQLtokenDataType } from './types';

const props = defineProps<{
  tockenBackendResponse: ManageTokenType;
  tokenSnippetData: MySQLtokenDataType;
}>();

console.log(props.tockenBackendResponse, 'tockenBackendResponse');
</script>
../types
