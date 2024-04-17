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
  token: props.tokenBackendResponse?.canarydrop?.canarytoken?._value || '',
  auth: props.tokenBackendResponse.canarydrop?.auth || '',
  appId: props.tokenBackendResponse.canarydrop?.app_id || '',
  displayName: props.tokenBackendResponse.canarydrop?.cert_name || '',
  fileWithCertAndPrivateKey:
    props.tokenBackendResponse.canarydrop?.cert_file_name || '',
  tenant: props.tokenBackendResponse.canarydrop?.tenant_id || '',
});
</script>
