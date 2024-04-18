<!-- TODO: fix the backend, adjust the frontend afterwards-->
<template>
  <!-- <div v-if="!tokenSnippet">Error loading</div>
  <TokenDisplay
    v-else
    :token-snippet="tokenSnippet"
  /> -->
  <BaseMessageBox variant="warning"
    >The token snippet is not available at the moment. We'll fix this
    soon.</BaseMessageBox
  >
</template>

<script lang="ts" setup>
// import { ref } from 'vue';
// import TokenDisplay from './TokenDisplay.vue';
// import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

// const props = defineProps<{
//   tokenBackendResponse: ManageTokenBackendType;
// }>();

// TODO: check how to get the snippet from tokenBackendResponse
// const tokenSnippet = ref('');
</script>
