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
  quickcreate_url:
    props.tokenBackendResponse.canarydrop?.aws_s3_quickcreate_url || '',
  bucket_name:
    props.tokenBackendResponse.canarydrop?.aws_s3_bucket_name || '',
  region:
    props.tokenBackendResponse.canarydrop?.aws_s3_region || '',
});
</script>
