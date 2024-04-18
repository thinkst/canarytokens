<!-- TODO: to fix once backend is adjusted and /manage returns the CSS snippet -->
<template>
  <!-- <div v-if="!tokenSnippet">Error loading</div>
  <TokenDisplay
    v-else
    :token-snippet="tokenSnippet"
  /> -->
  <BaseMessageBox variant="warning"
    >The CSS snippet is not available at the moment. We'll fix this
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

// const tokenSnippet = ref(props.tokenBackendResponse.canarydrop?.css);
</script>
