<template>
    <div class="grid layout-grid">
        <slot></slot>
    </div>
</template>

<script setup lang="ts"></script>

<style scoped>
.layout-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
}
</style>
