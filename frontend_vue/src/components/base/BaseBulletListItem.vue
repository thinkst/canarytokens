<template>
  <li
    class="grid justify-start grid-flow-col gap-8 px-16 py-8 text-left bg-white border rounded-2xl border-grey-200 text-grey-500"
  >
    <p><slot></slot></p>
  </li>
</template>

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
