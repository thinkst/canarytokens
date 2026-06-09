<template>
  <base-code-snippet
    lang="javascript"
    label="MCP configuration"
    :code="McpJson"
  ></base-code-snippet>
  <base-button
    class="mt-16"
    @click="handleDownloadMcpConfig"
    >Download mcp.json</base-button
  >
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { downloadAsset } from '@/api/main';

type McpDataType = {
  mcpjson: string;
  auth: string;
  token: string;
};

const props = defineProps<{
  tokenData: McpDataType;
}>();

const McpJson = ref(props.tokenData.mcpjson);

async function handleDownloadMcpConfig() {
  const params = {
    fmt: 'mcp',
    auth: props.tokenData?.auth,
    token: props.tokenData?.token,
  };
  try {
    const res = await downloadAsset(params);
    window.location.href = res.request.responseURL;
  } catch (err) {
    console.log(err, 'File download failed');
  } finally {
    console.log('Download ready');
  }
}
</script>
