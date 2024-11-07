<template>
  <div class="flex flex-col gap-16">
    <base-code-snippet
      lang="javascript"
      label="Login URL"
      is-single-line
      :code="tokenUrl"
    ></base-code-snippet>
    <base-code-snippet
      lang="javascript"
      label="Entity ID"
      is-single-line
      :code="entityId"
    ></base-code-snippet>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  tokenUrl: string;
  entityId: string;
}>();
</script>
