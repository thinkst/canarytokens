<template>
  Here it is
  <TokenSnippet :token-url="props.tokenSnippetData" />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenSnippet from './TokenSnippet.vue';
import type { ManageTokenType } from '@/components/types.ts';

const props = defineProps<{
  tockenBackendResponse: ManageTokenType;
  tokenSnippetData: string;
}>();

console.log(props, 'props!');
</script>
