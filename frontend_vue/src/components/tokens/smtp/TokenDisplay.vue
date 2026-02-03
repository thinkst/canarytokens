<template>
  <base-code-snippet
    lang="javascript"
    label="Email"
    :code="tokenData"
  ></base-code-snippet>
</template>

<script setup lang="ts">
defineProps<{
  tokenData: string;
}>();
</script>
