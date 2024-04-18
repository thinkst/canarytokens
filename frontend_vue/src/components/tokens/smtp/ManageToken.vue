<template>
  <div v-if="!tokenAuthData">Error loading</div>
  <TokenDisplay
    v-else
    :token-data="generatedEmail"
  />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenAuthData = ref({
  token: props.tokenBackendResponse?.canarydrop?.canarytoken?._value,
  hostname: props.tokenBackendResponse.canarydrop.generated_hostname || '',
});

const generatedEmail = `${tokenAuthData.value.token}@${tokenAuthData.value.hostname.split(/\.(.+)/)[1]}`;
</script>
