<template>
  <button
    class="relative flex flex-col items-center px-16 text-sm leading-relaxed duration-100 border rounded-2xl hover:border-green-500 active:border-green-500 group"
    :class="selected ? ' border-green-500 ' : 'border-grey-200'"
  >
    <font-awesome-icon
      v-if="selected"
      icon="xmark"
      class="absolute left-[8px] top-[.25rem] w-2rem text-green-500"
    ></font-awesome-icon>
    <span
      class="block capitalize group-hover:text-green-500"
      :class="selected ? 'text-green-500 pl-8' : 'text-grey-300 px-4'"
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
