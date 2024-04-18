<!-- TODO: fix after related backend task on /generate is solved-->
<template>
  <BaseMessageBox variant="warning">
    The token Snippet is Not available here at the moment. You can check it by
    clicking on Manage Token below.
  </BaseMessageBox>
  <p class="mt-16 text-sm">
    When the actions are run, your Canarytoken will be triggered.
  </p>
  <p class="mt-16 text-sm">
    Since DNS is used as the underlying transport, the Source IP will be that of
    a DNS server, not the database server.
  </p>
</template>

<script setup lang="ts">
// import TokenDisplay from './TokenDisplay.vue';
// import type { NewTokenBackendType } from '@/components/tokens/types';

// const props = defineProps<{
//   tokenData: NewTokenBackendType;
// }>();
</script>
