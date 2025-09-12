<template>
  <div
    v-if="showInyoni"
    class="flex flex-row items-center align justify-center w-[105%] wrapper relative inyoni_message"
    v-bind="$attrs"
  >
    <button
      v-if="!props.hideCloseButton"
      type="button"
      class="absolute w-24 h-24 text-sm duration-150 bg-white border border-solid rounded-full top-8 right-8 hover:text-white text-grey-300 border-grey-300 hover:bg-green-600 hover:border-green-300 z-10 close-button"
      @click="removeInyoni"
    >
      <font-awesome-icon
        icon="xmark"
        aria-hidden="true"
      />
      <span class="fa-sr-only">Close</span>
    </button>
    <img
      src="@/assets/inyoni.gif"
      alt="Inyoni"
      class="max-w-[6rem] mr-5 z-10 inyoni-gif"
    />
    <div
      class="border bg-white rounded-3xl border-grey-200 p-16 pl-24 italic baloon"
    >
      <p :class="`baloon-content-${contentId}`"></p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, toRef } from 'vue';
import { generateRandomString } from '@/utils/utils';

const props = defineProps<{
  text: string;
  hideCloseButton?: boolean;
}>();

const showInyoni = defineModel<boolean>();

onMounted(() => {
  comicBaloonContntAnimation();
});

const comicBaloonContent = toRef(props, 'text');
const contentId = generateRandomString(10);

function comicBaloonContntAnimation() {
  const arrayOfCharacters = comicBaloonContent.value.split('');
  const contentElement = document.querySelector(`.baloon-content-${contentId}`);
  const animationDelay = 1600;

  arrayOfCharacters.forEach((char, index) => {
    const span = document.createElement('span');
    span.textContent = char;
    span.style.opacity = '0';
    span.style.animation = 'fade-in 10ms ease-in forwards';
    span.style.animationDelay = `${animationDelay + index * 40}ms`;
    contentElement?.appendChild(span);
  });
}

function removeInyoni() {
  const balloonElement = document.querySelector('.baloon') as HTMLElement;
  const inyoniElement = document.querySelector('.inyoni-gif') as HTMLElement;
  const closeButtonElement = document.querySelector(
    '.close-button'
  ) as HTMLElement;

  inyoniElement.classList.add('fade-out');
  closeButtonElement.classList.add('fade-out');
  balloonElement.classList.add('baloon-exit');
  setTimeout(() => {
    showInyoni.value = false;
  }, 800);
}
</script>

<style scoped lang="scss">
@keyframes fade-in {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes fade-out {
  from {
    transform: scale(1);
    opacity: 1;
  }
  to {
    transform: scale(0.5);
    opacity: 0;
  }
}

@keyframes resize {
  from {
    transform: scale(0) translateX(-5%);
    opacity: 0;
  }
  to {
    transform: scale(1) translateX(-5%);
    opacity: 1;
  }
}

@keyframes resize-reverse {
  from {
    transform: scale(1) translateX(-5%);
    opacity: 1;
  }
  to {
    transform: scale(0) translateX(-5%);
    opacity: 0;
  }
}

.wrapper {
  container: inline-size;

  .inyoni-gif {
    opacity: 0;
    animation: fade-in 500ms ease-in forwards;
    animation-delay: 200ms;
  }

  .baloon {
    opacity: 0;
    animation: resize 800ms cubic-bezier(0.47, 1.64, 0.41, 0.8) forwards;
    animation-delay: 800ms;
    transform-origin: top left;
  }

  .baloon-exit {
    animation: resize-reverse 800ms cubic-bezier(0.47, 1.64, 0.41, 0.8) forwards;
    transform-origin: top left;
  }

  .close-button {
    opacity: 0;
    animation: fade-in 800ms ease-in forwards;
    animation-delay: 2000ms;
  }

  .fade-out {
    animation: fade-out 300ms ease-in forwards;
  }
}
</style>
