<template>
  <label
    :for="id"
    class="mb-4 ml-4 font-semibold"
  >
    <slot></slot>
    <span
      v-if="required"
      class="text-green-500"
    >
      *</span
    ></label
  >
</template>

<script setup lang="ts">
defineProps<{
  id: string;
  required?: boolean;
}>();
</script>
