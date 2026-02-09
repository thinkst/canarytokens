<template>
  <TokenDisplay :token-data="tokenData" />
  <p class="mt-16 text-sm">
    This token is triggered when someone accesses the decoy S3 bucket in your
    AWS account. The bucket is unique and monitored via CloudTrail. i.e. There
    is no chance of a false positive.
  </p>
  <ButtonActivateTokenTips @how-to-use="$emit('howToUse')" />

  <base-message-box
    class="mt-24"
    variant="info"
    :message="`If this token fires, it is a clear indication that someone is poking around in your AWS account.`"
  />
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

const tokenData = ref({
  quickcreate_url: props.tokenData.quickcreate_url || '',
  bucket_name: props.tokenData.bucket_name || '',
  region: props.tokenData.region || '',
});
</script>
