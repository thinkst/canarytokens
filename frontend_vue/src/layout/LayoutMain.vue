<template>
    <main class="flex items-center justify-center main-height bg-grey-50">
        <div class="flex-grow m-24 md:mx-[10svw] bg-white rounded-lg shadow-lg shadow-grey-200/40 min-h-[50vh] p-24">
            <slot ></slot>
        </div>
    </main>
</template>

<script setup lang="ts">
</script>

<style scoped>

.main-height {
  min-height: calc(100svh - (100px + 100px));
}
</style>
