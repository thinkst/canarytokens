<template>
  <TokenDisplay :token-snippet="tokenSnippetData" />
  <p class="mt-16 text-sm">
    Use this Javascript to detect when someone has cloned a webpage.
  </p>
  <BaseMessageBox
    class="mt-24"
    variant="info"
    message="When someone clones your site, they’ll grab this JavaScript too. When the script runs on their cloned site, it triggers an alert to let you know what’s going on."
    text-link="More tips?"
    @click="() => $emit('howToUse')"
  />
</template>

<script setup lang="ts">
import TokenDisplay from './TokenDisplay.vue';
import { ref } from 'vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

defineEmits(['howToUse']);

const tokenSnippetData = ref(props.tokenData.clonedsite_js || '');
</script>
