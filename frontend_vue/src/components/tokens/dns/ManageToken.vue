<template>
  <div v-if="!tokenUrl">Error loading</div>
  <TokenDisplay
    v-else
    :token-url="tokenUrl"
  />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tockenBackendResponse: ManageTokenBackendType;
}>();

const tokenUrl = ref(props.tockenBackendResponse.canarydrop?.generated_url);
</script>
