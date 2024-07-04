<template>
  <base-code-snippet
    lang="php"
    label="Canarytoken hostname"
    is-single-line
    :code="tokenUrl"
  ></base-code-snippet>
</template>

<script setup lang="ts">
defineProps<{
  tokenUrl: string;
}>();
</script>
