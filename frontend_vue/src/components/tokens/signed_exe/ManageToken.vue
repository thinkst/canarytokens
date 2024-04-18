<template>
  <div v-if="!tokenInfo">Error loading</div>
  <!-- <TokenDisplay
    v-else
    :token-data="tokenInfo"
  /> -->
  <BaseMessageBox variant="warning">
    Currently this token is not available for download, we will fix this
    soon.</BaseMessageBox
  >
</template>

<script lang="ts" setup>
import { ref } from 'vue';
// import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

// TODO: these fields are coming empty from the backend
const tokenInfo = ref({
  file_name: props.tokenBackendResponse.canarydrop.file_name || '',
  file_contents: props.tokenBackendResponse.canarydrop.file_contents || '',
});
</script>
