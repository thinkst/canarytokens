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

interface MySQLtokenBackendType extends NewTokenBackendType {
  usage: string;
  token: string;
  auth: string;
}

const props = defineProps<{
  tokenData: MySQLtokenBackendType;
}>();

const tokenSnippetData = ref({
  code: props.tokenData.usage || '',
  token: props.tokenData.token || '',
  auth: props.tokenData.auth_token || '',
});
</script>
