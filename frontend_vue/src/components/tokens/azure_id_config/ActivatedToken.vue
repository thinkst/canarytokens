<template>
  <!-- <TokenDisplay :token-data="tokenData" /> -->
  <p class="mt-16 text-sm">
    When someone clones your site, they'll load the token, which will check
    whether the referrer domain is expected. If not, it fires the token and you
    get an alert.
  </p>
  <base-message-box
    class="mt-24"
    variant="info"
    message="upload it as a custom branding stylesheet for your Azure Entra ID login portal (requires a P1 or P2 subscription)"
    text-link="How?"
    href="https://learn.microsoft.com/en-us/entra/fundamentals/how-to-customize-branding"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

// const props = defineProps<{
//   tokenData: NewTokenBackendType;
// }>();

// const tokenData = ref({
//   token: props.tokenData.token || '',
//   auth: props.tokenData.auth_token || '',
//   appId: props.tokenData.app_id || '',
//   displayName: props.tokenData.cert_name || '',
//   fileWithCertAndPrivateKey: props.tokenData.cert_file_name || '',
//   tenant: props.tokenData.tenant_id || '',
// });
</script>
