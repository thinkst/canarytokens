<template>
  <button
    class="flex flex-col items-center px-16 border sm:py-8 sm:px-16 grayscale hover:grayscale-0 rounded-2xl hover:border-green-500 active:border-green-500 group"
    :class="selected ? ' border-green-500 grayscale-0' : 'border-grey-200'"
  >
    <font-awesome-icon
      v-if="selected"
      icon="xmark"
      class="absolute sm:right-[8px] left-[8px] top-[.25rem] w-2rem text-green-500"
    ></font-awesome-icon>
    <img
      :src="filterLogo"
      alt="Filter icon"
      class="w-[2.5rem] not-sr-only group-hover:opacity-100 hidden sm:block"
      :class="selected ? 'opacity-100' : 'opacity-75'"
    />
    <span
      class="block capitalize sm:mt-8 group-hover:text-green-500 sm:p-0"
      :class="selected ? 'text-green-500 pl-8' : 'text-grey-300 px-4'"
      >{{ category }}</span
    >
  </button>
</template>

<script setup lang="ts">
import getImageUrl from '@/utils/getImageUrl';

const props = defineProps<{
  icon: string;
  category: string;
  selected: boolean;
}>();

const filterLogo = getImageUrl(`token_icons/${props.icon}`);
</script>
