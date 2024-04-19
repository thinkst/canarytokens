<template>
  <TokenDisplay :token-data="tokenSnippetData" />
  <p class="mt-24 text-sm text-center">
    You'll get an alert when someone tries to use your Kubeconfig.
  </p>
</template>

<script setup lang="ts">
import TokenDisplay from './TokenDisplay.vue';
import { ref } from 'vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

const tokenSnippetData = ref({
  token: props.tokenData.token || '',
  auth: props.tokenData.auth_token || '',
});
</script>
