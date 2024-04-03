<template>
  <base-code-snippet
    lang="php"
    label="URL token"
    :code="tokenUrl"
  ></base-code-snippet>
</template>

<script setup lang="ts">
defineProps<{
  tokenUrl: string;
}>();
</script>
