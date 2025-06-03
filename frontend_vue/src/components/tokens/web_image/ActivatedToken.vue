<template>
  <TokenDisplay :token-url="tokenUrl" />
  <p class="mt-16 text-sm">
    Remember, it gets triggered whenever someone requests the URL.
  </p>
  <base-message-box
    class="mt-24"
    variant="info"
    :message="`If this URL is requested as an image, your custom image will be served. If you've disabled your custom image on this Canarytoken's management page, then a 1x1 image is served instead.`"
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
