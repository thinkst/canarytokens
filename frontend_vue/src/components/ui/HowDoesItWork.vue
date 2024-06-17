<template>
  <ul class="sm:grid sm:grid-cols-[3fr_1fr_3fr_1fr_3fr] flex flex-col">
    <template
      v-for="(item, index) in items"
      :key="index"
    >
      <li class="flex flex-row sm:items-center sm:justify-start sm:flex-col">
        <span class="icon-shadow">
          <img
            :src="getImageUrl(item.imgSrc)"
            :alt="item.altText"
            class="h-[5rem] w-auto"
          />
        </span>
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
          class="arrow"
          :class="index === 0 ? 'self-start ' : 'self-center'"
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
  tokenServices[props.selectedToken].carouselSlides || []
);

const items = [
  {
    imgSrc: 'icons/howitworks_1.png',
    altText: 'Create it',
    header: 'Create it',
    paragraph: slideContent.value[0],
    arrowSrc: 'howitworks_arrow0.png',
  },
  {
    imgSrc: 'icons/howitworks_2.png',
    altText: 'Deploy it',
    header: 'Deploy it',
    paragraph: slideContent.value[1],
    arrowSrc: 'howitworks_arrow1.png',
  },
  {
    imgSrc: 'icons/howitworks_3.png',
    altText: 'It works!',
    header: 'It works!',
    paragraph: slideContent.value[2],
  },
];
</script>

<style scoped>
.arrow {
  transform: scale(1.8);
}

.icon-shadow::after {
  content: '';
  position: relative;
  display: inline-block;
  width: 5rem;
  height: 0.5rem;
  border-radius: 50%;
  @apply bg-grey-100;
  filter: blur(0.1rem);
  transform: scale(0.6) translateY(-0.5rem);
}
</style>
