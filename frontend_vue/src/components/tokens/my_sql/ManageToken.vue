<template>
  Your Token
  <div v-if="!tockenData">Error loading</div>
  <TokenDisplay
    v-else
    :token-data="tockenData"
  />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';
import generateManagedToken from '@/components/tokens/my_sql/generateManagedToken';

const props = defineProps<{
  tockenBackendResponse: ManageTokenBackendType;
}>();

const tockenData = ref({
  code: generateManagedToken(props.tockenBackendResponse),
  token: props.tockenBackendResponse?.canarydrop?.canarytoken?._value,
  auth: props.tockenBackendResponse.canarydrop?.auth,
});
</script>
