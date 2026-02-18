<template>
  <div v-if="!tokenData.svg">Error loading</div>
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
  token: props.tokenBackendResponse?.canarydrop?.canarytoken?._value || '',
  auth: props.tokenBackendResponse?.canarydrop?.auth || '',
  svg: props.tokenBackendResponse?.canarydrop?.svg || '',
});
</script>
