<template>
  <TokenDisplay :token-url="tokenUrl" />
  <p class="mt-16 text-sm">
    Remember, it gets triggered whenever someone requests the URL.
  </p>
  <base-message-box
    class="mt-24"
    variant="info"
    :message="`If this URL is requested as an image (e.g. <img src=''>), or if the request includes an Accept header that allows an image response, your custom image will be served. If you've disable your custom image on this Canarytoken's management page, then a 1x1 image is served instead.
    If you've enabled the browser scanner on this Canarytoken's management page, and the request includes an Accept header that allows HTML but not images, a blank HTML page containing fingerprinting JavaScript will be served. If the browser scanner is disabled, a HTML page displaying Earth will be returned.`"
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
