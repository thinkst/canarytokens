<template>
	<div id="cc-card" class="w-[280px] h-[11em] sm:w-[20.5em] sm:h-[13em] relative m-auto text-white">
		<span class="absolute top-[60px] sm:top-[75px] left-[20px] sm:left-[25px] text-base sm:text-lg">{{ props.tokenData.name_on_card }}</span>
		<span class="absolute top-[85px] sm:top-[100px] left-[20px] sm:left-[25px] text-base sm:text-lg">{{ formatCreditCardNumber(props.tokenData.card_number) }}</span>
		<span class="absolute top-[135px] sm:top-[160px] left-[20px] sm:left-[25px] text-base sm:text-lg">{{ props.tokenData.expiry_month }}/{{ props.tokenData.expiry_year }}</span>
		<span class="absolute top-[135px] sm:top-[160px] left-[135px] sm:left-[165px] text-base sm:text-lg">{{ props.tokenData.cvv }}</span>
	</div>
	<div class="grid grid-cols-6 p-16 text-sm grid-flow-row-dense gap-8 mt-24 items-center border border-grey-200 rounded-xl shadow-solid-shadow-grey">
		<BaseContentBlock
			class="col-span-6 xl:col-span-4" :label="'Card Name'" :text="props.tokenData.name_on_card" :icon-name="'id-card'" copy-content />
		<BaseContentBlock
			class="col-span-6 xl:col-span-4" :label="'Card Number'" :text="formatCreditCardNumber(props.tokenData.card_number)" :icon-name="'credit-card'" copy-content />
		<BaseContentBlock
			class="col-span-3 xl:col-span-2" :label="'Expires'" :text="`${props.tokenData.expiry_month}/${props.tokenData.expiry_year}`" :icon-name="'calendar-day'" copy-content />
		<BaseContentBlock
			class="col-span-3 xl:col-span-2" :label="'CVV'" :text="props.tokenData.cvv" :icon-name="'lock'" copy-content />
	</div>
</template>

<script setup lang="ts">
import { useClipboard } from "@vueuse/core";

export type CreditCardDataType = {
  auth: string;
  token: string;
  name_on_card: string;
  card_number: string;
  expiry_month: string;
  expiry_year: string;
  cvv: string;
};

const props = defineProps<{
	tokenData: CreditCardDataType;
}>();

const { isSupported, copy, copied } = useClipboard({
  //@ts-ignore
  content: props.content,
});

function formatCreditCardNumber(number: string) {
  return `${number.match(/(\d{4})/g)?.join(' ')}`;
}

</script>

<style lang="scss" scoped>
#cc-card {
  font-family: 'OCR A Extended';
  background-image: url('@/assets/credit-card-template.png');
  background-repeat: no-repeat;
  background-size: contain;
}
</style>
