<template>
  <TokenDisplay :token-url="tokenUrl" />
  <p class="mt-16 text-sm">
    The token is similar to the Fast Redirect token, however, when the link is
    loaded the user's browser / browser plugin information is captured.
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
