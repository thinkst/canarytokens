<template>
  <TokenDisplay :token-data="tokenData" :displayInfoBox="true"/>
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
</script>
