<template>
  <div v-if="!tokenData">Error loading</div>
  <TokenDisplay
    v-else
    :token-data="tokenData"
  />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';
import generateManagedToken from '@/components/tokens/my_sql/generateManagedToken';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenData = ref({
  code: generateManagedToken(props.tokenBackendResponse),
  token: props.tokenBackendResponse?.canarydrop?.canarytoken?._value,
  auth: props.tokenBackendResponse.canarydrop?.auth as string,
});
</script>
