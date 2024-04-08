<template>
  <div>QR code img</div>
  <p>{{ tokenPng }}</p>
</template>

<script setup lang="ts">
defineProps<{
  tokenPng: string;
}>();
</script>
