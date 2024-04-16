<template>
  <TokenDisplay :token-data="tokenData" />
  <p class="mt-16 text-sm">
    This canarytoken is triggered when someone uses this credential pair to
    access AWS programmatically (through the API). The key is unique. i.e. There
    is no chance of somebody guessing these credentials.
  </p>
  <base-message-box
    class="mt-24"
    variant="info"
    :message="`If this token fires, it is a clear indication that this set of keys has 'leaked'`"
  />
  <p class="mt-24 text-sm"></p>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

const tokenData = ref({
  aws_access_key_id: props.tokenData.aws_access_key_id || '',
  aws_secret_access_key: props.tokenData.aws_secret_access_key || '',
  output: props.tokenData.output || '',
  region: props.tokenData.region || '',
});
</script>
