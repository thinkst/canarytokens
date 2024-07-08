<template>
  <label
    :for="id"
    class="mb-4 ml-4 font-semibold">
    <slot></slot>
</label>
</template>

<script setup lang="ts">
defineProps<{
  id: string;
}>();
</script>
