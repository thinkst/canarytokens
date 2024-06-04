<template>
  <h3 class="mb-16 text-lg font-semibold leading-10 text-center text-grey-800">
    How do you want to deploy it?
  </h3>
  <TokenDisplay :token-data="tokenData" />
  <p class="mt-16 text-sm">
    When someone clones your site, they'll load the token, which will check
    whether the referrer domain is expected. If not, it fires the token and you
    get an alert.
  </p>
  <BaseMessageBox
    class="mt-24"
    variant="info"
    message="Upload it as a custom branding stylesheet for your Azure Entra ID login portal (requires a P1 or P2 subscription)"
    text-link="How?"
    href="https://learn.microsoft.com/en-us/entra/fundamentals/how-to-customize-branding"
    target="_blank"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { NewTokenBackendType } from '@/components/tokens/types';
import TokenDisplay from './TokenDisplay.vue';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

const tokenData = ref({
  token: props.tokenData.token || '',
  auth: props.tokenData.auth_token || '',
  client_id: props.tokenData.client_id || '',
  css: props.tokenData.css || '',
});
</script>
