<template>
  <li class="relative flex flex-1">
    <button
      class="relative group border flex flex-col group bg-white rounded-xl top-[0px] shadow-solid-shadow-grey border-grey-200 duration-100 ease-in-out token-card justify-between"
      @click.stop="handleClickToken"
    >
      <!-- content -->
      <div class="flex flex-col items-center px-16 pt-16 pb-24">
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
        <h3
          class="flex-grow py-16 font-semibold leading-5 text-center text-grey-800"
        >
          {{ title }}
        </h3>
        <p
          class="flex-grow text-sm leading-5 text-center text-grey-400 text-pretty"
        >
          {{ description }}
        </p>
      </div>
      <!--- cta --->
      <div
        class="w-full font-semibold bg-grey-50 text-grey-400 h-[3rem] rounded-b-xl transition duration-100 hover-card shadow-solid-shadow-grey card-button justify-center items-center flex"
      >
        Create Token
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

const logoUrl = toRef(props, 'logoImgUrl');
const isLoading = ref(true);
const src = ref('');

onMounted(() => {
  loadImage();
});

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

watch(logoUrl, () => {
  loadImage();
});
</script>

<style scoped>
.token-card:hover,
.token-card:focus,
.token-card:focus-within {
  @apply border-green shadow-solid-shadow-green-500-sm;
}

.card-button:focus {
  @apply from-green to-green-200 text-white border-b-green shadow-solid-shadow-green-500-sm bg-gradient-to-b outline-none;
}

.hover-card {
  @apply group-hover:from-green group-hover:to-green-200 group-hover:text-white group-hover:border-b-green group-hover:shadow-solid-shadow-green-500-sm group-hover:bg-gradient-to-b;
}
</style>
