<template>
  <TokenDisplay :token-data="tokenInfo" />
  <p class="mt-16 text-sm">
    Remember, this token is triggered whenever the binary file is executed. For
    EXEs, this means direct execution and for DLLs, it means they were loaded.
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

const tokenInfo = ref({
  file_name: props.tokenData.file_name || '',
  file_contents: props.tokenData.file_contents || '',
});
</script>
