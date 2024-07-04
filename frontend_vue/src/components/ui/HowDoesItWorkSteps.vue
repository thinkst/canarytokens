<template>
  <ul class="sm:grid sm:grid-cols-[3fr_1fr_3fr_1fr_3fr] flex flex-col">
    <template
      v-for="(item, index) in items"
      :key="index"
    >
      <li
        class="flex flex-row items-center flex-1 sm:justify-start sm:flex-col"
      >
        <img
          :src="getImageUrl(item.imgSrc)"
          :alt="item.altText"
          class="h-auto sm:w-[8rem]"
        />
        <div class="mt-16">
          <h3 class="px-16 text-sm font-semibold sm:text-center text-grey-700">
            {{ item.header }}
          </h3>
          <p class="px-16 text-sm sm:text-center text-grey-400 text-pretty">
            {{ item.paragraph }}
          </p>
        </div>
      </li>
      <span
        v-if="item.arrowSrc"
        :key="index"
        class="hidden sm:flex"
      >
        <img
          :src="getImageUrl(item.arrowSrc)"
          :alt="item.altText"
          class="self-start arrow"
          :class="index !== 0 && 'mt-[4rem]'"
        />
      </span>
    </template>
  </ul>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import getImageUrl from '@/utils/getImageUrl';
import { tokenServices } from '@/utils/tokenServices';

const props = defineProps<{
  selectedToken: string;
}>();

const slideContent = ref<string[]>(
  tokenServices[props.selectedToken].howItWorksInstructions || []
);

const items = [
  {
    imgSrc: 'icons/howitworks_step_1.png',
    altText: 'Create it',
    header: 'Create it',
    paragraph: slideContent.value[0],
    arrowSrc: 'howitworks_arrow_1.png',
  },
  {
    imgSrc: 'icons/howitworks_step_2.png',
    altText: 'Deploy it',
    header: 'Deploy it',
    paragraph: slideContent.value[1],
    arrowSrc: 'howitworks_arrow_2.png',
  },
  {
    imgSrc: 'icons/howitworks_step_3.png',
    altText: 'It works!',
    header: 'It works!',
    paragraph: slideContent.value[2],
  },
];
</script>

<style scoped>
.arrow {
  transform: scale(3.5);
}
</style>
