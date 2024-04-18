<template>
  <base-code-snippet
    lang="css"
    label="CSS token"
    :code="tokenSnippet"
    multiline
    custom-height="8rem"
  ></base-code-snippet>
</template>

<script setup lang="ts">
defineProps<{
  tokenSnippet: string;
}>();
</script>
