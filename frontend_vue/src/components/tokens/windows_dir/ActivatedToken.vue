<template>
  <TokenDisplay :token-data="tokenSnippetData" />
  <p class="mt-16 text-sm">
    Unzip this file in a folder, and get notified when someone browses the
    folder in Windows Explorer. It will even trigger if someone is browsing the
    folder via a network share!
    <ButtonActivateTokenTips @how-to-use="$emit('howToUse')" />
  </p>
  <base-message-box
    class="mt-32"
    :variant="'warning'"
    :message="`This token only works on Windows 10 systems and lower. It does
      not work on Windows 11 or higher. This is because a recent group policy update to
      some versions of Windows defaults to disabling functionality that this token
      relies on to fire.`"
  />
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
