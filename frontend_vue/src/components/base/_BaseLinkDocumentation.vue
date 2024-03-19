<template>
  <a
    class="inline-flex hover:text-green-700 text-grey-400 bg-transparent border border-solid rounded-full border-grey-200 hover:border-green-500 w-[1.2rem] h-[1.2rem] justify-center items-center my-8 mx-8"
    :href="link"
    target="_blank"
    :aria-label="`Check ${title} documentation`"
  >
    <font-awesome-icon
      icon="question"
      class="w-6 h-6 text-xs"
      aria-hidden="true"
    />
    <!-- Visually hides an element containing a text-equivalent for an icon
            while keeping it accessible to assisitive technologies
            https://docs.fontawesome.com/web/dig-deeper/accessibility
        -->
    <span class="fa-sr-only">Check documentation</span>
  </a>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    link: string;
    title?: string;
  }>(),
  {
    title: '',
  }
);
</script>
