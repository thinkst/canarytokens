<template>
	<div v-if="!tokenInfo">Error loading</div>
	<TokenDisplay v-else :token-data="tokenInfo" />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
	tokenBackendResponse: ManageTokenBackendType;
}>();

const tokenInfo = ref({
	name_on_card: props.tokenBackendResponse.canarydrop?.cc_v2_name_on_card || '',
	card_number: props.tokenBackendResponse.canarydrop?.cc_v2_card_number || '',
	expiry_month: props.tokenBackendResponse.canarydrop?.cc_v2_expiry_month || '',
	expiry_year: props.tokenBackendResponse.canarydrop?.cc_v2_expiry_year || '',
	cvv: props.tokenBackendResponse?.canarydrop.cc_v2_cvv || '',
});
</script>
