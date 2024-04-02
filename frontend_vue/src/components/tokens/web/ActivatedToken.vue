<template>
  <TokenSnippet :token-url="tokenSnippetData" />
  <p class="mt-16 text-sm">
    Remember, it gets triggered whenever someone requests the URL.
  </p>
  <base-message-box
    class="mt-24"
    variant="info"
    :message="`If the URL is requested as an image (e.g. <img src=''''>) then a 1x1 image is served. If the URL is surfed in a browser then a blank page is served with fingerprinting Javascript.`"
  />
  <p class="mt-24 text-sm"></p>
</template>

<script setup lang="ts">
import TokenSnippet from './TokenSnippet.vue';

defineProps<{
  tokenSnippetData: string;
}>();
</script>
