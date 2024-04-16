<template>
  <base-code-snippet
    lang="javascript"
    label="Log4j snippet"
    :code="tokenUsage"
  ></base-code-snippet>
</template>

<script setup lang="ts">
defineProps<{
  tokenUsage: string;
}>();
</script>
