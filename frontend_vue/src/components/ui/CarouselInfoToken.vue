<template>
  <h3 class="mt-16 text-lg font-semibold text-grey-400">How does it work?</h3>
  <div
    class="relative w-full sm:h-[100px] h-[110px] md:w-[90%] lg:w-[70%] carousel"
  >
    <ul class="flex flex-row mx-8 carousel__slides-container">
      <li
        v-for="(slide, index) in slideContent"
        :id="`${index + 1}__slide`"
        :key="slide"
        tabindex="0"
        class="flex-[0_0_100%] relative flex items-center my-16 bg-white border rounded-xl shadow-solid-shadow-grey border-grey-200 carousel__slide"
      >
        <img
          :src="getCarouselIcon(index)"
          alt="icon"
          aria-hidden="true"
          class="h-[3.5rem] sm:ml-16 ml-8"
        />
        <span class="carousel__slide__snapper"></span>
        <p class="px-16 text-sm text-left text-grey-400 text-pretty">
          {{ slide }}
        </p>
      </li>
    </ul>
  </div>
  <nav class="relative flex flex-row gap-16 carousel__nav">
    <button
      v-for="(_slide, index) in slideContent"
      :id="`${index + 1}__slide`"
      :key="index"
      :class="isActiveSlide(index) ? 'active' : ''"
      class="w-[1.8rem] h-[1.8rem] bg-grey-300 border-4 border-grey-100 rounded-full text-white font-semibold items-center flex justify-center hover:bg-grey-200 transition duration-150"
      @click="handleSlideChange(index + 1)"
    >
      {{ index + 1 }}
    </button>
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import getImageUrl from '@/utils/getImageUrl';
import { tokenServices } from '@/utils/tokenServices';

const props = defineProps<{
  selectedToken: string;
}>();

const slideContent = ref(
  tokenServices[props.selectedToken].carouselSlides || []
);
const currentSlide = ref(0);

onMounted(() => {
  const sliderView = document.querySelector('.carousel__slides-container');
  sliderView &&
    sliderView.addEventListener('scroll', () => {
      calculateActiveSlide(sliderView);
    });

  sliderView && calculateActiveSlide(sliderView);
});

// Show token icon for first slide, and carousel icon for the rest
function getCarouselIcon(index: number) {
  return index === 0
    ? getImageUrl(`token_icons/${tokenServices[props.selectedToken].icon}`)
    : getImageUrl(`icons/carousel_${index + 1}.png`);
}

function calculateActiveSlide(sliderView: Element) {
  const singleSlideWidth = sliderView
    ? sliderView.getBoundingClientRect().width
    : 0;

  // Hack: adding 10px to sliderView.scrollLeft fix issue on slideIndex calculation
  const scrollPosition = sliderView?.scrollLeft + 10 || 0;
  const slideIndex = Math.floor(scrollPosition / singleSlideWidth);

  currentSlide.value = slideIndex + 1;
}

function handleSlideChange(id: number) {
  const slide = document.getElementById(`${id}__slide`);
  slide && slide.scrollIntoView(false);
}

function isActiveSlide(index: number) {
  return index === currentSlide.value - 1;
}
</script>

<style>
.carousel__slides-container {
  @apply absolute top-0 right-0 bottom-0 left-0 flex overflow-x-scroll scroll-smooth snap-mandatory snap-x;
}

.carousel__slide__snapper {
  @apply absolute top-0 left-0 w-full h-full snap-center;
}

.active {
  @apply bg-green-500 border-green-200 hover:bg-green-500;
}

/* Remove Scrollbar style */

.carousel__slides-container {
  box-sizing: border-box;
  scrollbar-color: transparent transparent;
  scrollbar-width: 0px;
}

.carousel__slides-container::-webkit-scrollbar {
  width: 0;
}

.carousel__slides-container::-webkit-scrollbar-track {
  background: transparent;
}

.carousel__slides-container::-webkit-scrollbar-thumb {
  background: transparent;
  border: none;
}

.carousel__slides-container {
  -ms-overflow-style: none;
}
/* End Remove Scrollbar style */
</style>
