<template>
	<div class="flex flex-col items-center">
		<CreditCardToken
			:token-data="tokenData" />
		<base-button
			class="mt-24"
			:href="href"
			:download="download"
			@click="handleDownloadCC()">
			Download Credit Card
		</base-button>
	</div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import CreditCardToken from '@/components/ui/CreditCardToken.vue';
import type { CCtokenDataType } from '@/components/tokens/types.ts';

const props = defineProps<{
	tokenData: CCtokenDataType;
}>();

const href = ref('download?fmt=cc'+'&token=mwnioj2ijoij2223'+'&auth=wkoowmwojojoow')
const download = ref(props.tokenData.name_on_card.concat('_'))

const handleDownloadCC = () =>  {
	console.log('Download CC')
}
</script>
