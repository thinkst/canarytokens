<template>
  <TokenDisplay :token-data="tokenSnippetData" />
  <p class="mt-24 text-sm">
    You'll get an alert whenever this document is opened in Microsoft Office, on
    Windows or macOS.
    <ButtonActivateTokenTips @how-to-use="$emit('howToUse')" />
  </p>
  <base-message-box
    class="mt-24"
    variant="info"
    message="You can rename the document without affecting its operation."
  />
</template>

<script setup lang="ts">
import TokenDisplay from './TokenDisplay.vue';
import { ref } from 'vue';
import type { NewTokenBackendType } from '@/components/tokens/types';
import ButtonActivateTokenTips from '@/components/ui/ButtonActivateTokenTips.vue';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

defineEmits(['howToUse']);

const tokenSnippetData = ref({
  token: props.tokenData.token || '',
  auth: props.tokenData.auth_token || '',
});
</script>
