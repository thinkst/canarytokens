<template>
  <TokenDisplay :token-data="tokenData" :displayInfoBox="false"/>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenData = ref({
  token: props.tokenBackendResponse?.canarydrop?.canarytoken?._value || '',
  auth: props.tokenBackendResponse.canarydrop?.auth || '',
});
</script>
