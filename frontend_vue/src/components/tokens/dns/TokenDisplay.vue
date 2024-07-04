<template>
  <base-code-snippet
    lang="php"
    label="URL Canarytoken"
    is-single-line
    :code="tokenUrl"
  ></base-code-snippet>
</template>

<script setup lang="ts">
defineProps<{
  tokenUrl: string;
}>();
</script>
