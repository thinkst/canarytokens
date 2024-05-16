<template>
  <base-code-snippet
    lang="sql"
    label="Microsoft Server SQL token"
    :code="snippetCode"
    custom-height="10rem"
    show-expand-button
  ></base-code-snippet>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import generateSQLServertoken from './generateSQLServertoken';
import type { SQLServerDataType } from './types';

const props = defineProps<{
  tokenData: SQLServerDataType;
}>();

const SQLData = ref({
  hostname: props.tokenData.hostname,
  sql_table_name: props.tokenData.sql_table_name,
  sql_trigger_name: props.tokenData.sql_trigger_name,
  sql_function_name: props.tokenData.sql_function_name,
  sql_server_view_name: props.tokenData.sql_server_view_name,
  sql_action: props.tokenData.sql_action,
});

const snippetCode = generateSQLServertoken(SQLData.value);
</script>
