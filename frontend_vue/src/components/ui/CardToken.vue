<template>
  <li class="relative flex token-card-wrapper">
    <button
      class="group border flex flex-1 flex-col group bg-grey-50 rounded-xl top-[0px] shadow-solid-shadow-grey border-grey-200 duration-100 ease-in-out justify-between token-card items-center"
      @click.stop="handleClickToken"
      @mouseover="handleMouseOver"
      @focus="handleMouseOver"
      @mouseleave="handleMouseLeave"
      @blur="handleMouseLeave"
    >
      <!-- Content -->
      <div class="flex flex-col items-center px-16 pt-16">
        <div v-if="isLoading">
          <BaseSkeletonLoader
            type="circle"
            class="w-[4rem] h-[4rem]"
          />
        </div>
        <img
          v-if="!isLoading"
          :src="src"
          class="h-[4.5rem] transition-transform duration-150 group-hover:scale-105"
          aria-hidden="true"
          :alt="`${title} logo`"
        />

        <p
          class="flex-grow py-16 text-sm text-center text-grey-400 text-pretty"
        >
          {{ description }}
        </p>
      </div>
      <!--- CTA text --->
      <div
        class="w-full px-16 leading-5 font-semibold bg-white text-grey-400 h-[3rem] rounded-b-xl transition duration-100 hover-card shadow-solid-shadow-grey card-button justify-center items-center flex"
      >
        {{ isHoverCard ? 'Create Token' : title }}
      </div>
    </button>
    <BaseButtonHowToDeploy
      :token-name="title"
      :is-open="false"
      size="big"
      class="absolute bottom-8 right-8 z-10 top-[9px]"
      @click="handleHowToUseButton"
    />
  </li>
</template>

<script setup lang="ts">
import { onMounted, ref, toRef, watch } from 'vue';
import getImageUrl from '@/utils/getImageUrl';
import { useModal } from 'vue-final-modal';
import ModalToken from '@/components/ModalToken.vue';

const emit = defineEmits(['clickToken']);

const props = withDefaults(
  defineProps<{
    description: string;
    title: string;
    logoImgUrl: string;
    selectedToken: string | number;
  }>(),
  {
    logoImgUrl: 'default.png',
  }
);

const logoUrl = toRef(props, 'logoImgUrl');
const isLoading = ref(true);
const src = ref('');
const isHoverCard = ref(false);

onMounted(() => {
  loadImage();
});

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

async function loadImage() {
  src.value = '';
  isLoading.value = true;
  const img = new Image();
  const tokenLogoUrl = getImageUrl(`token_icons/${logoUrl.value}`);
  img.src = tokenLogoUrl;
  await new Promise((resolve) => (img.onload = resolve));
  src.value = img.src;
  isLoading.value = false;
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

watch(logoUrl, () => {
  loadImage();
});
</script>

<style scoped lang="scss">
.token-card:hover,
.token-card:focus,
.token-card:focus-within {
  @apply border-green shadow-solid-shadow-green-500-sm;

  .card-button {
    @apply from-green to-green-200 text-white border-b-green shadow-solid-shadow-green-500-sm bg-gradient-to-b outline-none;
  }
}
</style>
