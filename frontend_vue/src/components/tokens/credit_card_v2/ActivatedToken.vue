<template>
	<base-message-box
		v-if="!tokenData"
		class="mt-24" variant="info"
		:message="`Credit card token not available yet'`" />
	<TokenDisplay v-else :token-data="tokenData" />
	<base-message-box
		class="mt-24" variant="info"
		:message="`If the card number is ever used in an authorization, the transaction will be declined, but you will be alerted.'`" />
	<p class="mt-24 text-sm"></p>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { CCtokenDataType } from '@/components/tokens/types.ts';

const props = defineProps<{
	tokenData: CCtokenDataType;
}>();

const tokenData = ref({
	name_on_card: props.tokenData.name_on_card || '',
	card_number: props.tokenData.card_number || '',
	expiry_month: props.tokenData.expiry_month || '',
	expiry_year: props.tokenData.expiry_year || '',
	cvv: props.tokenData.cvv || '',
});
</script>
