<template>
  <TokenDisplay :token-data="tokenData" />
  <p class="mt-16 text-sm">
    This token is triggered when someone uses this credential pair to
    authenticate against the CrowdStrike API. The client ID is unique. i.e.
    There is no chance of somebody guessing these credentials.
  </p>
  <ButtonActivateTokenTips @how-to-use="$emit('howToUse')" />

  <base-message-box
    class="mt-24"
    variant="info"
    :message="`If this token fires, it is a clear indication that these CrowdStrike API credentials have leaked.`"
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
  client_id: props.tokenData.client_id || '',
  client_secret: props.tokenData.client_secret || '',
  base_url: props.tokenData.base_url || '',
});
</script>
