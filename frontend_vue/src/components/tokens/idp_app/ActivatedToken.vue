<template>
  <TokenDisplay
    :token-url="tokenUrl"
    :entity-id="entityId"
    :app-type="appType"
  />
  <p class="mt-16 text-sm">
    When the fake app is opened from your IdP dashboard you receive an alert.
    <ButtonActivateTokenTips @how-to-use="$emit('howToUse')" />
  </p>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { NewTokenBackendType } from '@/components/tokens/types';
import ButtonActivateTokenTips from '@/components/ui/ButtonActivateTokenTips.vue';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

defineEmits(['howToUse']);

const tokenUrl = ref(props.tokenData.token_url || '');
const entityId = ref(props.tokenData.entity_id || '');
const appType = ref(props.tokenData.app_type || '');
</script>
