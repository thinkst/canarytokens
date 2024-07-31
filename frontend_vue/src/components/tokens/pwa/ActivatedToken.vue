<template>
  <TokenDisplay :token-url="tokenUrl" />
  <p class="mt-16 text-sm">
    Remember, it gets triggered whenever someone opens the app.
  </p>
  <base-message-box
    class="mt-24"
    variant="info"
    :message="`When you open the token link on your phone, press 'Share', then 'Add to Home Screen' to install.`"
    text-link="More tips?"
    @click="() => $emit('howToUse')"
  />
  <p class="mt-24 text-sm"></p>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

defineEmits(['howToUse']);

const tokenUrl = ref(props.tokenData.token_url);
</script>
