<template>
  <TokenDisplay :token-data="tokenCode" />
  <p class="mt-16 text-sm">
    Remember, it gets triggered whenever someone clones the SVN repo.
  </p>
  <base-message-box
    class="mt-24"
    variant="warning"
    :message="`Don't forget to run the following command after you've added the token:`"
  />
  <BaseCodeSnippet
    class="mt-16"
    lang="bash"
    code="svn commit"
  ></BaseCodeSnippet>
  <p class="mt-24 text-sm">
    The source IP address shown in the alert is the DNS server, not the end
    user. <ButtonActivateTokenTips @how-to-use="$emit('howToUse')" />
  </p>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { NewTokenBackendType } from '@/components/tokens/types';
import generateSVNToken from './generateSVNToken.ts';
import ButtonActivateTokenTips from '@/components/ui/ButtonActivateTokenTips.vue';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

defineEmits(['howToUse']);

const tokenHostname = ref(props.tokenData.hostname);

const tokenCode = computed(() => {
  return tokenHostname.value ? generateSVNToken(tokenHostname.value) : '';
});
</script>
