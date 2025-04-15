<template>
  <li class="relative flex token-card-wrapper">
    <button
      ref="assetCardRef"
      class="group border flex flex-1 flex-col group bg-white rounded-2xl top-[0px] shadow-solid-shadow-grey border-grey-200 duration-100 ease-in-out justify-between asset-card items-center"
      @click.stop="handleClickToken"
      @mouseover="handleMouseOver"
      @focus="handleMouseOver"
      @mouseleave="handleMouseLeave"
      @blur="handleMouseLeave"
    >
      <!-- Content -->
      <div class="relative flex flex-col items-center gap-8 px-16 pt-16">
        <p
          class="flex-grow py-16 text-sm text-center text-grey-400 text-pretty"
        >
          Description
        </p>
      </div>
      <!--- CTA text --->
      <div
        class="w-full leading-5 font-semibold border-t-2 border-grey-50 text-grey-700 h-[3rem] rounded-b-2xl transition duration-100 hover-card shadow-solid-shadow-grey card-button justify-center items-center flex px-8"
      >
        {{ isHoverCard ? 'Edit' : assetType }}
      </div>
    </button>
  </li>
</template>

<script lang="ts" setup>
import { ref } from 'vue';

const emit = defineEmits(['clickAsset']);

const props = defineProps<{
  assetType: string;
}>();

const isHoverCard = ref(false);
const assetCardRef = ref();

function handleClickToken() {
  emit('clickAsset');
  // remove focus from selected card
  if (assetCardRef.value) {
    assetCardRef.value.blur();
  }
}

function handleMouseOver() {
  isHoverCard.value = true;
}

function handleMouseLeave() {
  isHoverCard.value = false;
}
</script>

<style></style>
