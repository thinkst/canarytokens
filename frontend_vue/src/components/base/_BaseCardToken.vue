<template>
  <div
    ref="tokenCardRef"
    class="group relative border flex flex-col px-24 py-32 bg-white rounded-xl top-[0px] shadow-solid-shadow-grey border-grey-200 items-center duration-100 ease-in-out token-card"
    role="button"
    tabindex="0"
    @click.stop="handleClickToken"
    @keyup.enter.stop="handleClickToken"
  >
    <img
      src="@/assets/token_icons/s3_bucket.png"
      class="w-[4rem]"
    />
    <h2 class="py-16 font-semibold leading-5 text-center text-grey-800">
      {{ title }}
    </h2>
    <p class="leading-5 text-grey-400 text-balance">
      {{ description }}
    </p>
    <button
      type="button"
      class="absolute border-none group-hover:right-[15px] group-focus:right-[15px] hover:right-[15px] focus:right-[15px] focus:opacity-100 bottom-[10px] py-8 px-8 focus:border opacity-0 right-[0] group-hover:opacity-100 group-focus:opacity-100 transition-all"
      @click.stop="handleClickToken"
      @keyup.enter.stop="handleClickToken"
      @focus="handleFocus"
      @blur="handleBlur"
    >
      <font-awesome-icon
        icon="arrow-right"
        class="text-green-500"
        aria-hidden="true"
      />
      <span class="fa-sr-only">Add {{ title }}</span>
    </button>
    <BaseLinkDocumentation
      :link="documentationLink"
      class="absolute top-[15px] left-[15px]"
      @focus="handleFocus"
      @blur="handleBlur"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  description: string;
  title: string;
  logo: string;
  documentationLink: string;
}>();

const emit = defineEmits(['clickToken']);

const tokenCardRef = ref<HTMLElement | null>(null);

function handleClickToken(e: Event) {
  emit('clickToken');
  e.preventDefault();
  e.stopPropagation();
  console.log(`selected ${props.title} token`);
}

// handleFocus and handleBlur add and remove styles to the card
// for consistant keyboard navigation and mouse hover

function handleFocus() {
  if (tokenCardRef.value !== null) {
    tokenCardRef.value.classList.add('focus-card');
  }
}
function handleBlur() {
  if (tokenCardRef.value !== null) {
    tokenCardRef.value.classList.remove('focus-card');
  }
}
</script>

<style scoped>
.focus-card,
.token-card:hover,
.token-card:focus {
  @apply border-green top-[-0.45rem] shadow-solid-shadow-green-500-md;
}
</style>
