<template>
  <div v-if="!tokenCode">Error loading</div>
  <TokenDisplay
    v-else
    :token-data="tokenCode"
  />
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';
import generateSVNToken from './generateSVNToken.ts';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenHostname = ref(
  props.tokenBackendResponse.canarydrop?.generated_hostname
);

const tokenCode = computed(
  () => tokenHostname.value && generateSVNToken(tokenHostname.value)
);
</script>
