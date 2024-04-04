<template>
  <p>There are two ways you can use this token:</p>
  <TokenDisplay :token-data="tokenSnippetData" />
  <base-message-box
    class="mt-24"
    variant="info"
    message="When the MySQL statements are run, your Canarytoken will be triggered."
  />
</template>

<script setup lang="ts">
import TokenDisplay from './TokenDisplay.vue';
import type { MySQLtokenDataType } from '../types';

defineProps<{
  tokenSnippetData: MySQLtokenDataType;
}>();
</script>
