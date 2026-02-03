<template>
  <ul class="grid layout-grid">
    <slot></slot>
  </ul>
</template>

<script setup lang="ts"></script>

<style scoped>
.layout-grid {
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.2rem;
}
</style>
