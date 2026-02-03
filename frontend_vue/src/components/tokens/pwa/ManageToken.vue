<template>
  <div v-if="!tokenSnippetData">Error loading</div>
  <TokenDisplay
    v-else
    :token-data="tokenSnippetData"
  />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenSnippetData = ref({
  url: props.tokenBackendResponse.canarydrop?.generated_url || '',
  pwa_icon: props.tokenBackendResponse.canarydrop?.pwa_icon || '',
  pwa_app_name: props.tokenBackendResponse.canarydrop?.pwa_app_name || '',
});
</script>
