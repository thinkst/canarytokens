<template>
  <p>There are two ways you can use this token:</p>
  <TokenDisplay :token-data="tokenSnippetData" />
  <base-message-box
    class="mt-24"
    variant="info"
    message="When the MySQL statements are run, your Canarytoken will be triggered."
  />
</template>

<script setup lang="ts">
import TokenDisplay from './TokenDisplay.vue';
import { ref } from 'vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

const tokenSnippetData = ref({
  hostname: props.tokenData.hostname || '',
  token: props.tokenData.token || '',
  auth: props.tokenData.auth_token || '',
  encoded: true,
});
</script>
