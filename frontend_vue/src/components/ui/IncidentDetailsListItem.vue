<template>
  <li>
    <span class="block text-xs uppercase text-grey-500">{{ label }}</span>
    <span :class="highlightBoolean(value)">{{ value }}</span>
  </li>
</template>

<script setup lang="ts">
defineProps<{
  label?: string | number;
  value: string | boolean | number;
}>();

/**
 * Returns a CSS class name based on the boolean value of the input parameter.
 */
function highlightBoolean(val: string | number | boolean) {
  if (typeof val === 'boolean') {
    return val ? 'text-green' : 'text-red';
  }
}
</script>
