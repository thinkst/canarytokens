<template>
  <button
    class="px-16 py-8 border sm:px-32 grayscale hover:grayscale-0 rounded-2xl hover:border-green-500 active:border-green-500 group"
    :class="selected ? ' border-green-500 grayscale-0' : 'border-grey-200'"
  >
    <font-awesome-icon
      v-if="selected"
      icon="xmark"
      class="absolute right-[8px] w-2rem text-green-500"
    ></font-awesome-icon>
    <img
      :src="filterLogo"
      alt="Filter icon"
      class="w-[3rem] not-sr-only group-hover:opacity-100"
      :class="selected ? 'opacity-100' : 'opacity-75'"
    />
    <span
      class="block mt-8 capitalize group-hover:text-green-500"
      :class="selected ? 'text-green-500' : 'text-grey-300'"
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

console.log(props.selected, 'selected');

const filterLogo = getImageUrl(`token_icons/${props.icon}`);
</script>
