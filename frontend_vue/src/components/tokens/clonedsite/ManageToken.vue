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

const tokenSnippet = ref(props.tokenBackendResponse.clonedsite_js);
</script>
