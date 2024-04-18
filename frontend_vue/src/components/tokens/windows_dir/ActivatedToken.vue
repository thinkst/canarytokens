<template>
  <TokenDisplay :token-data="tokenSnippetData" />
  <p class="mt-16 text-sm">
    Unzip this file in a folder, and get notified when someone browses the
    folder in Windows Explorer. It will even trigger if someone is browsing the
    folder via a network share!
  </p>
  <base-message-box
    class="mt-24"
    variant="info"
    :message="`The alert will include the network domain and username of the browsing user, if present.`"
  />
  <p class="mt-24 text-sm"></p>
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
