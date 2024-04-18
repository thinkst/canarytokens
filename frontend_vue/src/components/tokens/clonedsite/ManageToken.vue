<template>
  <div v-if="!tokenSnippet">Error loading</div>
  <TokenDisplay
    v-else
    :token-snippet="tokenSnippet"
  />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

// TODO: check how to get the snippet from tokenBackendResponse
const tokenSnippet = ref('');
</script>
