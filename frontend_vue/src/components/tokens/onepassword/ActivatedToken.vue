<template>
  <TokenDisplay :token-data="tokenData" />
  <p class="mt-16 text-sm">
    This token is triggered when someone attempts to use this saved credential.
    The M365 username is unique.
  </p>
  <ButtonActivateTokenTips @how-to-use="$emit('howToUse')" />

  <base-message-box
    class="mt-24"
    variant="info"
    :message="`If this token fires, it is a clear indication that this credential has 'leaked'`"
  />
  <p class="mt-24 text-sm"></p>
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

const tokenData = ref({email_addr: props.tokenData.email_addr || '', token: props.tokenData.token || '',
  auth: props.tokenData.auth_token || '',});
</script>
