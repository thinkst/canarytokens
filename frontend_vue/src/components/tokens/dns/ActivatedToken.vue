<template>
  <TokenDisplay :token-url="tokenUrl" />
  <p class="mt-16 text-sm">
    Remember, it gets triggered whenever someone performs a DNS lookup of the
    hostname.
    <ButtonActivateTokenTips @how-to-use="$emit('howToUse')" />
  </p>
  <base-message-box
    class="mt-24"
    variant="info"
    :message="`The source IP address shown in the alert is the DNS server, not the end user.`"
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

const tokenUrl = ref(props.tokenData.hostname || '');
</script>
