<template>
  <TokenDisplay :token-url="tokenUrl" />
  <p class="mt-16 text-sm">
    Remember, it gets triggered whenever someone requests the URL.
  </p>
  <base-message-box
    class="mt-24"
    variant="info"
    :message="`If the URL is requested as an image (e.g. <img src=''>) or if the URL is requested with an Accept header that for an image response then your custom image will be served. If you disable your custom image, (in this Canarytoken's manage page) then a 1x1 image is served instead.
    If you enable browser scanner, (in this Canarytoken's manage page) and the URL is requested with an Accept header that allows an HTML response and does not allow an image response, then a blank page is served with fingerprinting Javascript. If you disable browser scanner, then an HTML page showing Earth will be returned.`"
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
