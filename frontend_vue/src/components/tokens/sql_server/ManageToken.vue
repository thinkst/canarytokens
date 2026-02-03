<template>
  <div v-if="!tokenData">Error loading</div>
  <TokenDisplay
    v-else
    :token-data="tokenData"
  />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenData = ref({
  hostname: props.tokenBackendResponse.canarydrop?.generated_hostname,
  sql_table_name: props.tokenBackendResponse.canarydrop?.sql_server_table_name,
  sql_trigger_name:
    props.tokenBackendResponse.canarydrop?.sql_server_trigger_name,
  sql_function_name:
    props.tokenBackendResponse?.canarydrop?.sql_server_function_name,
  sql_server_view_name:
    props.tokenBackendResponse.canarydrop?.sql_server_view_name,
  sql_action: props.tokenBackendResponse.canarydrop?.sql_server_sql_action,
});
</script>
