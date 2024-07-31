<template>
	<div v-if="!tokenInfo">Error loading</div>
	<TokenDisplay v-else :token-data="tokenInfo" />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
	tokenData: ManageTokenBackendType;
}>();

// TODO: these fields are coming empty from the backend
// const tokenData = ref({
// 	card_name: props.tokenData.card_name || 'Paul Ndegwa Gichuki',
// 	card_number: props.tokenData.card_number || '0000 0000 0000 0000 0000',
// 	expiry: props.tokenData.expiry || '11/27',
// 	cvc: props.tokenData.cvc || '344',
// });

const tokenInfo = ref({
	card_name: 'Paul Ndegwa Gichuki',
	card_number:'0000 0000 0000 0000',
	expiry: '11/2027',
	cvc: '344',
});
</script>
