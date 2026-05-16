<template>
  <div v-if="!tokenData">Error loading</div>
  <TokenDisplay
    v-else
    :token-data="tokenData"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';
import TokenDisplay from './TokenDisplay.vue';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenData = ref({
  auth: props.tokenBackendResponse.canarydrop.auth || '',
  token: props.tokenBackendResponse.canarydrop.canarytoken._value || '',
  npm_token: props.tokenBackendResponse.canarydrop.npm_token || '',
  npm_package_name: props.tokenBackendResponse.canarydrop.npm_package_name || '',
  npm_package_version:
    props.tokenBackendResponse.canarydrop.npm_package_version || '',
});
</script>
