<!-- TODO: fix after related backend task on /generate is solved-->
<template>
  <TokenDisplay :token-data="tokenCode" />
  <p class="mt-16 text-sm">
    When the actions are run, your Canarytoken will be triggered.
  </p>
  <p class="mt-16 text-sm">
    Since DNS is used as the underlying transport, the Source IP will be that of
    a DNS server, not the database server.
  </p>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

const tokenCode = ref({
  hostname: props.tokenData.hostname || '',
  sql_table_name: props.tokenData.sql_server_table_name || '',
  sql_trigger_name: props.tokenData.sql_server_trigger_name || '',
  sql_function_name: props.tokenData?.sql_server_function_name || '',
  sql_server_view_name: props.tokenData.sql_server_view_name || '',
  sql_action: props.tokenData.sql_server_sql_action || '',
});
</script>
