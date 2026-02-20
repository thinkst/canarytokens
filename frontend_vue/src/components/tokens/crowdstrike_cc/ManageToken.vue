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
  client_id:
    props.tokenBackendResponse.canarydrop?.crowdstrike_client_id || '',
  client_secret:
    props.tokenBackendResponse.canarydrop?.crowdstrike_client_secret || '',
  base_url:
    props.tokenBackendResponse.canarydrop?.crowdstrike_base_url || '',
});
</script>
