<template>
  <div v-if="!tokenData">Error loading</div>
  <TokenDisplay
    v-else
    :token-data="tokenData"
  />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenData = ref({
  gcp_keyfile:
    props.tokenBackendResponse.canarydrop.gcp_keyfile || '',
  gcp_service_account_email: props.tokenBackendResponse.canarydrop.gcp_service_account_email || '',
});
</script>
