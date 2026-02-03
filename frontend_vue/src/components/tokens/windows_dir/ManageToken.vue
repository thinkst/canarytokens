<template>
  <div v-if="!tokenData">Error loading</div>
  <TokenDisplay
    v-else
    :token-data="tokenData"
  />
  <BaseMessageBox
    class="mt-32"
    :variant="'warning'"
    :message="`This token only works on Windows 10 systems and lower. It does
      not work on Windows 11 or higher. This is because a recent group policy update to
      some versions of Windows defaults to disabling functionality that this token
      relies on to fire.`" />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenData = ref({
  token: props.tokenBackendResponse?.canarydrop?.canarytoken?._value || '',
  auth: props.tokenBackendResponse.canarydrop?.auth || '',
});
</script>
