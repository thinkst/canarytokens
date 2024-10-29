<template>
  <div class="flex flex-col items-center min-h-[448px] justify-center">
    <div v-if="!showTestForm">
      <CreditCardToken
        :token-data="tokenData" />
      <div class="flex justify-center gap-16">
        <base-button
          variant="secondary"
          class="mt-24"
          @click="handleDownloadCC()">
          Download Credit Card
        </base-button>
        <base-button
          class="mt-24"
          @click="showTestForm = !showTestForm">
          Test Credit Card
        </base-button>
      </div>
    </div>
    <TriggerDemo
      v-else
      @close="showTestForm = false"
      :token-data="tokenData" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import CreditCardToken from '@/components/tokens/credit_card_v2/CreditCardToken.vue';
import type { CreditCardDataType } from '@/components/tokens/credit_card_v2/CreditCardToken.vue';
import TriggerDemo from '@/components/tokens/credit_card_v2/TriggerDemo.vue';
import { downloadAsset } from '@/api/main';

const props = defineProps<{
  tokenData: CreditCardDataType;
}>();

const showTestForm = ref(false);

async function handleDownloadCC() {
  const params = {
    fmt: 'credit_card_v2',
    auth: props.tokenData?.auth,
    token: props.tokenData?.token,
  };

  try {
    const res = await downloadAsset(params);
    window.location.href = res.request.responseURL;
  } catch (err) {
    console.log(err, 'File download failed');
  } finally {
    console.log('Download ready');
  }
}
</script>
