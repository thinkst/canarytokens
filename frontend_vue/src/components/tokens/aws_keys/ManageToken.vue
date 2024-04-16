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
  aws_access_key_id:
    props.tokenBackendResponse.canarydrop.aws_access_key_id || '',
  aws_secret_access_key:
    props.tokenBackendResponse.canarydrop.aws_secret_access_key || '',
  output: props.tokenBackendResponse.canarydrop.aws_output || '',
  region: props.tokenBackendResponse.canarydrop.aws_region || '',
});
</script>
