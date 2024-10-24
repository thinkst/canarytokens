<template>
	<div class="flex flex-col items-center">
		<CreditCardToken
			:token-data="tokenData" />
		<base-button
			class="mt-24"
			@click="handleDownloadCC()">
			Download Credit Card
		</base-button>
	</div>
</template>

<script setup lang="ts">
import CreditCardToken from '@/components/ui/CreditCardToken.vue';
import type { CreditCardDataType } from '@/components/ui/CreditCardToken.vue';
import { downloadAsset } from '@/api/main';

const props = defineProps<{
	tokenData: CreditCardDataType;
}>();

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
