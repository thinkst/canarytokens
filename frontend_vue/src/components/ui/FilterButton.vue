<template>
  <button
    class="relative flex flex-col items-center px-16 text-sm leading-relaxed duration-100 border rounded-2xl hover:border-green-500 active:border-green-500 group"
    :class="selected ? ' border-green-500 bg-green-100' : 'border-grey-200'"
  >
    <span
      class="block capitalize group-hover:text-green-500"
      :class="selected ? 'text-green-500 font-semibold' : 'text-grey-300'"
      >{{ category }}</span
    >
  </button>
</template>

<script setup lang="ts">
defineProps<{
  category: string;
  selected: boolean;
}>();
</script>
