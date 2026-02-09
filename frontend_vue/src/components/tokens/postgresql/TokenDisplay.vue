<template>
  <base-code-snippet
    class="mt-16"
    lang="bash"
    label="PostgreSQL connection string"
    :code="connectionString"
  ></base-code-snippet>
  <base-button
    class="mt-16"
    @click="handleDownloadPgpass"
    >Download .pgpass file</base-button
  >
</template>

<script setup lang="ts">
import { computed } from 'vue';

type PostgreSQLTokenDataType = {
  username: string;
  password: string;
  server: string;
  port: number;
};

const props = defineProps<{
  tokenData: PostgreSQLTokenDataType;
}>();

const connectionString = computed(
  () =>
    `postgresql://${props.tokenData.username}:${encodeURIComponent(props.tokenData.password)}@${props.tokenData.server}:${props.tokenData.port}/postgres`
);

function handleDownloadPgpass() {
  const content = `${props.tokenData.server}:${props.tokenData.port}:*:${props.tokenData.username}:${props.tokenData.password}`;
  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = '.pgpass';
  a.click();
  URL.revokeObjectURL(url);
}
</script>
