<template>
  <li class="relative flex token-card-wrapper">
    <button
      ref="cardTokenRef"
      class="group border flex flex-1 flex-col group bg-white rounded-2xl top-[0px] shadow-solid-shadow-grey border-grey-200 duration-100 ease-in-out justify-between token-card items-center"
      @click.stop="hadndleChangeAccountValues"
    >
      <!-- Content -->
      <div class="relative flex flex-col items-center gap-8 px-16 pt-16">
        <img
          :src="getImageUrl('aws_icon.svg')"
          alt="asw-token-icon"
          class="w-[4.5rem] h-[4.5rem]"
        />
        <ul class="mb-16">
          <li class="text-md text-grey-400">
            AWS account:
            <span class="text-grey font-semibold">{{
              props.tokenData.aws_account_number
            }}</span>
          </li>
          <li class="text-md text-grey-400">
            AWS region:
            <span class="text-grey font-semibold">{{
              props.tokenData.aws_region
            }}</span>
          </li>
        </ul>
      </div>
      <!--- CTA text --->
      <div
        class="w-full leading-5 font-semibold border-t-2 border-grey-50 text-grey-700 h-[3rem] rounded-b-2xl transition duration-100 hover-card shadow-solid-shadow-grey card-button justify-center items-center flex px-8"
      >
        Edit
      </div>
    </button>
  </li>
</template>

<script setup lang="ts">
import { defineAsyncComponent } from 'vue';
import { useModal } from 'vue-final-modal';
import type { TokenDataType } from '@/utils/dataService';
import type { GenericObject } from 'vee-validate';
import getImageUrl from '@/utils/getImageUrl.ts';

const ModalEditAWSInfo = defineAsyncComponent(
  () => import('./ModalEditAWSInfo.vue')
);

const emit = defineEmits(['saveEditData']);

const props = defineProps<{
  tokenData: TokenDataType;
}>();

function hadndleChangeAccountValues() {
  const { open, close } = useModal({
    component: ModalEditAWSInfo,
    attrs: {
      closeModal: () => close(),
      saveData: (data: GenericObject) => emit('saveEditData', data),
      tokenData: props.tokenData,
    },
  });
  open();
}
</script>

<style scoped lang="scss">
.token-card:hover,
.token-card:focus,
.token-card:focus-within {
  @apply border-green-600 shadow-solid-shadow-green-600-sm;

  .card-button {
    @apply text-white border-b-green-600 shadow-solid-shadow-green-600-sm bg-green-500 outline-none;
  }
}
</style>
