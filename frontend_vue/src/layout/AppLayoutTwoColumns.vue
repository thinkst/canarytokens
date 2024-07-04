<template>
  <div class="grid two-col-grid">
    <slot />
  </div>
</template>

<script setup lang="ts"></script>

<style>
.two-col-grid {
  grid-template-columns: 1fr 2fr;
  gap: 1rem;
}

@media screen and (max-width: 761px) {
  .two-col-grid {
    grid-template-columns: 100%;
    gap: 1rem;
  }

  .two-col-grid > #alerts-card-list {
    order: 2;
  }
}
</style>
