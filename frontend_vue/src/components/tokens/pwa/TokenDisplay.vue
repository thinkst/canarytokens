<template>
  <div class="flex justify-center">
    <base-button
      class="w-full mt-16"
      :href="tokenUrl"
      :download="tokenUrl"
      target="_blank"
      >Download Fake App Canarytoken</base-button
    >
  </div>
</template>

<script setup lang="ts">
defineProps<{
  tokenUrl: string;
}>();
</script>
