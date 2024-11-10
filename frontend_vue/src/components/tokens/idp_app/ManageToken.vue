<template>
  <div v-if="!tokenUrl || !entityId">Error loading</div>
  <TokenDisplay
    v-else
    :token-url="tokenUrl"
    :entity-id="entityId"
  />
  <BaseMessageBox
    variant="info"
    class="mt-32"
    >Select an app to download an icon to use for the fake app on your IdP dashboard.</BaseMessageBox
  >
  <CreateAppPreview />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';
import CreateAppPreview from './CreateAppPreview.vue';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenUrl = ref(props.tokenBackendResponse.canarydrop?.generated_url);
const entityId = ref(props.tokenBackendResponse.canarydrop?.idp_app_entity_id);
</script>
