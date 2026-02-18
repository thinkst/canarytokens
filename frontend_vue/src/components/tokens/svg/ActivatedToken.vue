<template>
  <TokenDisplay :token-data="tokenSnippetData"/>
  <p class="mt-16 text-sm">
    Remember, it gets triggered whenever someone loads the image.
  </p>
  <base-message-box
    class="mt-24"
    variant="info"
    :message="`When the image is loaded, a 1px square GIF is served.`"
    text-link="More tips?"
    @click="() => $emit('howToUse')"
  />
  <p class="mt-24 text-sm"></p>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

type AuthDataType = {
  auth: string;
  token: string;
};

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

defineEmits(['howToUse']);

const tokenSnippetData = ref({
  token: props.tokenData.token || '',
  auth: props.tokenData.auth_token || '',
  svg: props.tokenData.svg || '',
});
</script>
