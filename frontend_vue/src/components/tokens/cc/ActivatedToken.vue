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
	card_name: props.tokenData.card_name || 'Paul Ndegwa Gichuki',
	card_number: props.tokenData.card_number || '0000 0000 0000 0000',
	expiry: props.tokenData.expiry || '11/2027',
	cvc: props.tokenData.cvc || '344',
});
</script>
