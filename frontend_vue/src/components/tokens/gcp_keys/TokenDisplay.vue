<template>
  <base-code-snippet
    lang="json"
    label="AWS token"
    :code="GCPKeyCode"
  ></base-code-snippet>
</template>

<script setup lang="ts">
import { ref } from 'vue';

type GCPKeysDataType = {
  gcp_keyfile: string;
  gcp_service_account_email: string;
};

const props = defineProps<{
  tokenData: GCPKeysDataType;
}>();
const GCPKeyCode = ref(`${props.tokenData.gcp_keyfile}`);
</script>
