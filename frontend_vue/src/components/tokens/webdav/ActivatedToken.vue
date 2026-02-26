<template>
  <TokenDisplay :token-data="tokenCode" />
  <p class="mt-16 text-sm">
    When files are downloaded from the WebDAV folder, your Canarytoken will be triggered.
  </p>
  <p class="mt-16 text-sm">
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

const tokenCode = ref({
  hostname: props.tokenData.hostname || '',
  webdav_fs_type: props.tokenData.webdav_fs_type || '',
  webdav_password: props.tokenData.webdav_password || '',
  webdav_server: props.tokenData.webdav_server || '',
});
</script>
