<template>
  <base-message-box
    class="mt-24"
    variant="warning"
    message="In order to ensure that the token setup works ensure you
    are running the powershell script as admin."
  />
  <TokenDisplay :token-data="tokenData" />
  <base-message-box
    class="mt-24"
    variant="info"
    message="Once installed (with admin permissions) you'll get an alert whenever someone
  (or someone's code) accesses or copies files in your fake file system. It will automatically
  provide the file that was accessed, and the process used to access or copy the file."
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

const tokenData = ref({
  token: props.tokenData.token || '',
  auth: props.tokenData.auth_token || '',
});

const recommendedReg = ref(
  'reg import FILENAME /reg:64  \nreg import FILENAME /reg:32'
);
</script>
