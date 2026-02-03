<template>
  <TokenDisplay :token-data="tokenSnippetData" />
  <base-message-box
    class="mt-24"
    variant="info"
    :message="`Remember, it gets triggered whenever someone sends an email to the address.`"
    text-link="More tips?"
    @click="() => $emit('howToUse')"
  />
  <p class="mt-24 text-sm"></p>
</template>

<script setup lang="ts">
import TokenDisplay from './TokenDisplay.vue';
import { ref } from 'vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

defineEmits(['howToUse']);

const tokenSnippetData = ref(props.tokenData.unique_email || '');
</script>
