<template>
  <TokenDisplay :token-data="tokenSnippetData" />
  <base-message-box
    class="mt-24"
    variant="info"
    message="If this token fires, it is a clear indication that these credentials have been stolen."
    text-link="More tips?"
    @click="() => $emit('howToUse')"
  />
</template>

<script setup lang="ts">
import TokenDisplay from './TokenDisplay.vue';
import { ref } from 'vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

defineEmits(['howToUse']);

const tokenSnippetData = ref({
  username: props.tokenData.postgresql_username || '',
  password: props.tokenData.postgresql_password || '',
  server: props.tokenData.postgresql_server || '',
  port: props.tokenData.postgresql_port || 5432,
});
</script>
