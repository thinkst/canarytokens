<template>
  <TokenDisplay
    :token-url="tokenUrl"
    :entity-id="entityId"
    :app-type="appType"
  />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenUrl = ref(props.tokenBackendResponse.canarydrop?.generated_url || '');
const entityId = ref(props.tokenBackendResponse.canarydrop?.idp_app_entity_id || '');
const appType = ref(props.tokenBackendResponse.canarydrop?.idp_app_type || '');
</script>
