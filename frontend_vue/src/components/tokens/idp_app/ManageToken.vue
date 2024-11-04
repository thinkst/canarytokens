<template>
  <div v-if="!tokenUrl || !entityId">Error loading</div>
  <TokenDisplay
    v-else
    :token-url="tokenUrl"
    :entity-id="entityId"
  />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenUrl = ref(props.tokenBackendResponse.canarydrop?.generated_url);
const entityId = ref(props.tokenBackendResponse.canarydrop?.idp_app_entity_id);
</script>
