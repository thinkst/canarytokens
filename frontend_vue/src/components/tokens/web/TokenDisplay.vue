<template>
  <base-code-snippet
    lang="javascript"
    label="URL token"
    is-single-line
    :code="tokenUrl"
  ></base-code-snippet>
</template>

<script setup lang="ts">
defineProps<{
  tokenUrl: string;
}>();
</script>
