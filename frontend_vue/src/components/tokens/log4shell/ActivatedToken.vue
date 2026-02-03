<template>
  <TokenDisplay :token-usage="tokenUsage" />
  <p class="mt-16 text-sm">
    If the log line is consumed by a vulnerable log4j library, it will generate
    an alert on this token.
  </p>
  <p class="mt-16 text-sm">
    If this works, you will also obtain the hostname of the vulnerable server.
  </p>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

const tokenUsage = ref(props.tokenData.token_usage);
</script>
