<template>
  <TokenDisplay :token-data="tokenSnippetData" />
  <p class="mt-24 text-sm text-center">
    You'll get an alert when someone tries to use your Kubeconfig.
    <ButtonActivateTokenTips @how-to-use="$emit('howToUse')" />
  </p>
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
