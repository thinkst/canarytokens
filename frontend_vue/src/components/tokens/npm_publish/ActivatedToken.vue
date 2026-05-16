<template>
  <TokenDisplay :token-data="tokenData" />
  <p class="mt-16 text-sm">
    This token is meant to look like a real <code>NPM_TOKEN</code> for a canary
    package release. If that version ever gets published, you know the token was
    used.
  </p>
  <ButtonActivateTokenTips @how-to-use="$emit('howToUse')" />

  <base-message-box
    class="mt-24"
    variant="info"
    :message="`Keep the token as NPM_TOKEN and place the downloaded workspace next to it for a believable publish target.`"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { NewTokenBackendType } from '@/components/tokens/types';
import ButtonActivateTokenTips from '@/components/ui/ButtonActivateTokenTips.vue';
import TokenDisplay from './TokenDisplay.vue';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

defineEmits(['howToUse']);

const tokenData = ref({
  auth: props.tokenData.auth_token || '',
  token: props.tokenData.token || '',
  npm_token: props.tokenData.npm_token || '',
  npm_package_name: props.tokenData.npm_package_name || '',
  npm_package_version: props.tokenData.npm_package_version || '',
});
</script>
