<template>
  <TokenDisplay :token-data="tokenData" />
  <p class="mt-16 text-sm">
    This token is triggered when someone uses this Service Principal Login to
    access Azure programmatically (through the API).
  </p>
  <p class="mt-16 text-sm">
    The Service Principal Login is unique. i.e. There is no chance of somebody
    guessing these credentials.
  </p>
  <ButtonActivateTokenTips @how-to-use="$emit('howToUse')" />

  <base-message-box
    class="mt-24"
    variant="info"
    :message="`If this token fires, it is a clear indication that this set of keys has 'leaked'`"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { NewTokenBackendType } from '@/components/tokens/types';
import ButtonActivateTokenTips from '@/components/ui/ButtonActivateTokenTips.vue';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

defineEmits(['howToUse']);

const tokenData = ref({
  token: props.tokenData.token || '',
  auth: props.tokenData.auth_token || '',
  appId: props.tokenData.app_id || '',
  displayName: props.tokenData.cert_name || '',
  fileWithCertAndPrivateKey: props.tokenData.cert_file_name || '',
  tenant: props.tokenData.tenant_id || '',
});
</script>
