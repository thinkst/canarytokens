<template>
  <li class="relative flex">
    <button
      class="relative group border flex-1 group flex flex-col px-16 pt-16 pb-24 bg-white rounded-xl top-[0px] shadow-solid-shadow-grey-sm border-grey-200 items-center duration-100 ease-in-out token-card"
      @click.stop="handleClickToken"
    >
      <div v-if="isLoading">
        <BaseSkeletonLoader
          type="circle"
          class="w-[4rem] h-[4rem]"
        />
      </div>
      <img
        v-if="!isLoading"
        :src="src"
        class="h-[4rem] transition-transform duration-150 group-hover:scale-95"
        aria-hidden="true"
        :alt="`${title} logo`"
      />
      <span
        class="flex-grow py-16 font-semibold leading-5 text-center text-grey-800"
      >
        {{ title }}
      </span>
      <span
        class="flex-grow text-sm leading-5 text-center text-grey-400 text-pretty"
      >
        {{ description }}
      </span>
      <span
        class="absolute border-none group-hover:right-[8px] group-focus:right-[8px] hover:right-[8px] focus:right-[8px] focus:opacity-100 py-8 px-8 focus:border opacity-0 right-[0] bottom-[0] group-hover:opacity-100 group-focus:opacity-100 transition-all"
      >
        <font-awesome-icon
          icon="arrow-right"
          class="hidden text-green-500 sm:block"
          aria-hidden="true"
        />
        <span class="hidden fa-sr-only sm:block">Add {{ title }}</span>
      </span>
      <span
        class="flex flex-row items-center gap-8 mt-24 font-semibold text-green-600 sm:hidden"
        >Add Canarytoken
        <font-awesome-icon
          icon="arrow-right"
          class="text-green-500"
          aria-hidden="true"
      /></span>
    </button>

    <BaseLinkDocumentation
      :link="documentationLink"
      class="absolute z-10 top-[9px] left-[8px] cursor-pointer transition-all duration-100 ease-in-out token-card__documentation-link"
      tabindex="0"
      :title="title"
    />
  </li>
</template>

<script setup lang="ts">
import { onMounted, ref, toRef, watch } from 'vue';
import getImageUrl from '@/utils/getImageUrl';

const emit = defineEmits(['clickToken']);

const props = withDefaults(
  defineProps<{
    description: string;
    title: string;
    logoImgUrl: string;
    documentationLink: string;
  }>(),
  {
    logoImgUrl: 'default.png',
  }
);

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
  await new Promise(
    (resolve) => ((img.onload = resolve), console.log(resolve, 'resolve'))
  );
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
.token-card:focus {
  @apply border-green shadow-solid-shadow-green-500-sm ;
}
</style>
