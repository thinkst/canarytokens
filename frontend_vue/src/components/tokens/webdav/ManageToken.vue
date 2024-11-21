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
  hostname: props.tokenBackendResponse.canarydrop?.generated_hostname,
  webdav_fs_type: props.tokenBackendResponse.canarydrop?.webdav_fs_type,
  webdav_password: props.tokenBackendResponse.canarydrop?.webdav_password || '',
  webdav_server: props.tokenBackendResponse.canarydrop?.webdav_server || '',
});
</script>
