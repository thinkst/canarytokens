<template>
  <TokenDisplay :token-snippet="tokenSnippet" />
  <p class="mt-16 text-sm">
    Use this CSS to detect when someone has cloned a webpage.
  </p>
  <p class="mt-16 text-sm">
    When someone clones your site, they'll load the token, which will check
    whether the referrer domain is expected. If not, it fires the token and you
    get an alert.
  </p>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

const tokenSnippet = ref(props.tokenData.css || '');
</script>
