<template>
  <div class="grid two-col-grid">
    <slot />
  </div>
</template>

<scritp setup lang="ts"></scritp>

<style>
.two-col-grid {
  grid-template-columns: 1fr 2fr;
  gap: 1rem;
}
</style>
