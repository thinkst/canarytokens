<template>
  <base-code-snippet
    lang="bash"
    label="SVN command"
    :code="tokenData"
  ></base-code-snippet>
</template>

<script setup lang="ts">
defineProps<{
  tokenData: string;
}>();
</script>
