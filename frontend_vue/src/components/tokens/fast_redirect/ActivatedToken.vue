<template>
  <TokenDisplay :token-url="tokenUrl" />
  <p class="mt-16 text-sm">
    The token is similar to the Web token, however, when the link is loaded the
    view will be immediately redirected to the specified redirect URL.
  </p>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

const tokenUrl = ref(props.tokenData.token_url);
</script>
