<template>
  <button
    v-tooltip="{
      content: `Show ${categoryTitleCase} ${categoryType}`,
      popperClass: 'whitespace-nowrap ',
    }"
    v-bind="$attrs"
    class="relative flex flex-col items-center px-16 text-sm leading-relaxed duration-100 border rounded-2xl hover:border-green-500 active:border-green-500 group"
    :class="selected ? ' border-green-500 bg-green-100' : 'border-grey-200'"
  >
    <span
      class="block capitalize group-hover:text-green-500"
      :class="[
        { 'text-green-700': selected },
        { 'text-grey-400': !selected && !highContrast },
        { 'text-grey-500': !selected && highContrast },
      ]"
      >{{ category }}</span
    >
  </button>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

const props = defineProps<{
  category: string;
  categoryType: string;
  selected: boolean;
  highContrast?: boolean;
}>();

const categoryName = ref(props.category);

const categoryTitleCase = computed(() => {
  return (
    categoryName.value.charAt(0).toUpperCase() + categoryName.value.slice(1)
  );
});
</script>
