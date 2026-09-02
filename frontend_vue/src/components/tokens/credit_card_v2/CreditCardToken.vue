<template>
  <div
    id="cc-card"
    class="w-[280px] h-[11em] sm:w-[20.5em] sm:h-[13em] relative m-auto text-white"
    :class="{ 'grayscale opacity-70': props.isExpired }"
  >
    <span class="absolute top-[60px] sm:top-[75px] left-[20px] sm:left-[25px] text-base sm:text-lg">{{ props.tokenData.name_on_card }}</span>
    <span class="absolute top-[85px] sm:top-[100px] left-[20px] sm:left-[25px] text-base sm:text-lg">{{ formatCreditCardNumber(props.tokenData.card_number) }}</span>
    <span class="absolute top-[135px] sm:top-[160px] left-[20px] sm:left-[25px] text-base sm:text-lg">{{ props.tokenData.expiry_month }}/{{ props.tokenData.expiry_year }}</span>
    <span class="absolute top-[135px] sm:top-[160px] left-[135px] sm:left-[165px] text-base sm:text-lg">{{ props.tokenData.cvv }}</span>
  </div>
  <div
    v-if="props.isExpired"
    class="flex flex-col items-center gap-16 px-24 py-32 mt-32 text-center border border-grey-200 rounded-xl shadow-solid-shadow-grey bg-white"
  >
    <img
      src="@/assets/icons/credit-card-token/credit-card-expired.png"
      class="w-[4rem] h-[4rem]"
      alt="Expired credit card"
    />
    <p class="font-semibold text-grey-900">This credit card token has expired.</p>
    <p class="max-w-[24rem] leading-6 text-grey-500">
      To continue receiving alerts, simply create a new Credit Card Canarytoken at
      <a class="font-bold text-grey-500" href="https://canarytokens.org">Canarytokens.org</a>
      and replace the expiring token in your environment.
    </p>
  </div>
  <div class="grid grid-cols-6 p-16 text-sm grid-flow-row-dense gap-8 mt-32 items-center border border-grey-200 rounded-xl shadow-solid-shadow-grey bg-white">
    <BaseContentBlock
      class="col-span-6 xl:col-span-6" :label="'Card Name'" :text="props.tokenData.name_on_card" :icon-name="'id-card'" :copy-button-fill-color="copyButtonFillColor" copy-content />
    <BaseContentBlock
      class="col-span-6 xl:col-span-6" :label="'Card Number'" :text="formatCreditCardNumber(props.tokenData.card_number)" :icon-name="'credit-card'" :copy-button-fill-color="copyButtonFillColor" copy-content />
    <BaseContentBlock
      class="col-span-6 lg:col-span-3" :label="'Expires'" :text="`${props.tokenData.expiry_month}/${props.tokenData.expiry_year}`" :icon-name="'calendar-day'" :copy-button-fill-color="copyButtonFillColor" copy-content />
    <BaseContentBlock
      class="col-span-6 lg:col-span-3" :label="'CVV'" :text="props.tokenData.cvv" :icon-name="'lock'" :copy-button-fill-color="copyButtonFillColor" copy-content />
  </div>
</template>

<script setup lang="ts">
export type CreditCardDataType = {
  auth: string;
  token: string;
  card_id: string;
  name_on_card: string;
  card_number: string;
  expiry_month: string;
  expiry_year: string;
  cvv: string;
};

const props = defineProps<{
  tokenData: CreditCardDataType;
  isExpired: boolean;
}>();

const copyButtonFillColor = props.isExpired ? 'grey' : 'green';

const emits = defineEmits(['close']);

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
