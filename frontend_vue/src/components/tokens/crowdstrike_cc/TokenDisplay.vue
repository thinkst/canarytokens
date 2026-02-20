<template>
  <base-code-snippet
    lang="json"
    label="CrowdStrike API credentials"
    :code="credentialsJson"
  ></base-code-snippet>
  <base-button
    class="mt-16"
    @click="handleDownloadCredentials"
    >Download credentials</base-button
  >
  <base-code-snippet
    class="mt-16"
    lang="bash"
    label="Example usage"
    :code="curlExample"
  ></base-code-snippet>
</template>

<script setup lang="ts">
import { ref } from 'vue';

type CrowdStrikeCCDataType = {
  client_id: string;
  client_secret: string;
  base_url: string;
};

const props = defineProps<{
  tokenData: CrowdStrikeCCDataType;
}>();

const credentialsJson = ref(JSON.stringify({
  client_id: props.tokenData.client_id,
  client_secret: props.tokenData.client_secret,
  base_url: props.tokenData.base_url,
}, null, 2));

const curlExample = ref(`curl -X POST "${props.tokenData.base_url}/oauth2/token" \\
  -H "accept: application/json" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "client_id=${props.tokenData.client_id}&client_secret=${props.tokenData.client_secret}"`);

function handleDownloadCredentials() {
  const blob = new Blob([credentialsJson.value], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'crowdstrike_credentials.json';
  a.click();
  URL.revokeObjectURL(url);
}
</script>
