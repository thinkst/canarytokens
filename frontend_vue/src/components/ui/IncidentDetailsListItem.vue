<template>
  <li>
    <span class="block text-xs uppercase text-grey-500">{{ label }}</span>
    <span>{{ value }}</span>
  </li>
</template>

<script setup lang="ts">
defineProps<{
  label?: string | number;
  value: string | boolean | number;
}>();
</script>
