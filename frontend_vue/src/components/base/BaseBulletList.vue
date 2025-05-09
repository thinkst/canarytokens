<template>
  <ul class="flex flex-col w-full gap-16 my-16 items-left text-grey-800">
    <li
      v-for="item in props.list"
      :key="item"
      class="grid justify-start grid-flow-col gap-8 px-16 py-8 text-left bg-white border rounded-2xl border-grey-200 text-grey-500"
    >
      {{ item }}
    </li>
  </ul>
</template>

<script lang="ts" setup>
const props = defineProps<{
  list: string[];
}>();
</script>

<style scoped>
li::before {
  font-family: 'Font Awesome 6 Free';
  content: '\f0e7';
  @apply text-green-500;
}
p :deep(li) {
  list-style-type: disc;
}
p :deep(code) {
  @apply bg-green-100 px-8 py-[2px] rounded-md mt-4;
  overflow-wrap: anywhere;
}
</style>