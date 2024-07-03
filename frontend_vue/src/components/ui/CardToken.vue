<template>
  <li class="relative flex token-card-wrapper">
    <button
      class="group border flex flex-1 flex-col group bg-white rounded-2xl top-[0px] shadow-solid-shadow-grey border-grey-200 duration-100 ease-in-out justify-between token-card items-center"
      @click.stop="handleClickToken"
      @mouseover="handleMouseOver"
      @focus="handleMouseOver"
      @mouseleave="handleMouseLeave"
      @blur="handleMouseLeave"
    >
      <!-- Content -->
      <div class="relative flex flex-col items-center gap-8 px-16 pt-16">
        <TokenIcon
          :title="title"
          :logo-img-url="props.logoImgUrl"
          class="w-[4.2rem] h-[4.2rem]"
          :is-interacted="isHoverCard"
          :has-shadow="true"
        />
        <p
          class="flex-grow py-16 text-sm text-center text-grey-400 text-pretty"
        >
          {{ description }}
        </p>
      </div>
      <!--- CTA text --->
      <div
        class="w-full leading-5 font-semibold border-t-2 border-grey-50 text-grey-700 h-[3rem] rounded-b-2xl transition duration-100 hover-card shadow-solid-shadow-grey card-button justify-center items-center flex px-8"
      >
        {{ isHoverCard ? 'Create Token' : title }}
      </div>
    </button>
    <ButtonHowToDeploy
      :token-name="title"
      :is-open="false"
      size="big"
      class="absolute bottom-8 right-8 z-10 top-[9px]"
      @click="handleHowToUseButton"
    />
  </li>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useModal } from 'vue-final-modal';
import ModalToken from '@/components/ModalToken.vue';
import TokenIcon from '@/components/icons/TokenIcon.vue';
import ButtonHowToDeploy from '@/components/ui/ButtonHowToDeploy.vue';

const emit = defineEmits(['clickToken']);

const props = defineProps<{
  description: string;
  title: string;
  logoImgUrl: string;
  selectedToken: string | number;
}>();

const isHoverCard = ref(false);

function handleHowToUseButton() {
  const { open, close } = useModal({
    component: ModalToken,
    attrs: {
      selectedToken: props.selectedToken as string,
      closeModal: () => close(),
      selectedModalType: 'howToUse',
    },
  });
  open();
}

function handleClickToken() {
  emit('clickToken');
}

function handleMouseOver() {
  isHoverCard.value = true;
}

function handleMouseLeave() {
  isHoverCard.value = false;
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
