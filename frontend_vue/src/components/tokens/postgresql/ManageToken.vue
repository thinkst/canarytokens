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

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenData = ref({
  username: props.tokenBackendResponse.canarydrop.postgresql_username || '',
  password: props.tokenBackendResponse.canarydrop.postgresql_password || '',
  server: props.tokenBackendResponse.canarydrop.postgresql_server || '',
  port: props.tokenBackendResponse.canarydrop.postgresql_port || 5432,
});
</script>
