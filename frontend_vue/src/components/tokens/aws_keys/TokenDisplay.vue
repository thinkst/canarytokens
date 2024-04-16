<template>
  <base-code-snippet
    lang="javascript"
    label="AWS token"
    :code="AWSKeyCode"
    multiline
    custom-height="100px"
  ></base-code-snippet>
</template>

<script setup lang="ts">
import { ref } from 'vue';

type AWSKeysDataType = {
  aws_access_key_id: string;
  aws_secret_access_key: string;
  output: string;
  region: string;
};

const props = defineProps<{
  tokenData: AWSKeysDataType;
}>();

const AWSKeyCode = ref(`[default]
aws_access_key_id = ${props.tokenData.aws_access_key_id}
aws_secret_access_key = ${props.tokenData.aws_secret_access_key}
output = ${props.tokenData.output}
region = ${props.tokenData.region}`);
</script>
