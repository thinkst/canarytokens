<template>
  <button
    class="inline-block text-sm cursor-pointer text-green hover:text-green-600"
    @click="$emit('howToUse')"
  >
    Need more tips?
  </button>
</template>

<script setup lang="ts">
defineEmits(['howToUse']);
</script>
