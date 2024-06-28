<template>
	<div id="cc-card" class="w-[280px] h-[11em] sm:w-[20.5em] sm:h-[13em] relative m-auto text-white">
		<span class="absolute top-[50px] sm:top-[65px] left-[20px] sm:left-[25px]">{{ props.tokenData.card_name }}</span>
		<span class="absolute top-[75px] sm:top-[90px] left-[20px] sm:left-[25px]">{{ props.tokenData.card_number }}</span>
		<span class="absolute top-[135px] sm:top-[160px] left-[20px] sm:left-[25px]">{{ props.tokenData.expiry }}</span>
		<span class="absolute top-[135px] sm:top-[160px] left-[135px] sm:left-[165px]">{{ props.tokenData.cvc }}</span>
	</div>
	<div class="grid grid-cols-6 p-16 text-sm grid-flow-row-dense gap-8 mt-24 items-center border border-grey-200 rounded-xl shadow-solid-shadow-grey">
		<BaseContentBlock
			class="col-span-6 sm:col-span-4" :label="'Card Name'" :text="props.tokenData.card_name" :icon-name="'id-card'" copy-content />
		<BaseContentBlock
			class="col-span-6 sm:col-span-4" :label="'Card Number'" :text="props.tokenData.card_number" :icon-name="'credit-card'" copy-content />
		<BaseContentBlock
			class="col-span-3 sm:col-span-2" :label="'Expires'" :text="props.tokenData.expiry" :icon-name="'calendar-day'" copy-content />
		<BaseContentBlock
			class="col-span-3 sm:col-span-2" :label="'CVC'" :text="props.tokenData.cvc" :icon-name="'lock'" copy-content />
	</div>
</template>

<script setup lang="ts">
import { useClipboard } from "@vueuse/core";
import type { CCtokenDataType } from '@/components/tokens/types.ts';

const props = defineProps<{
	tokenData: CCtokenDataType;
}>();

const { isSupported, copy, copied } = useClipboard({
  //@ts-ignore
  content: props.content,
});

</script>

<style lang="scss" scoped>
#cc-card {
  font-family: 'OCR A Extended';
  background-image: url('@/assets/cc-background-AMEX.png');
  background-repeat: no-repeat;
  background-size: contain;
}
</style>
