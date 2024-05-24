<template>
  <RouterLink
    to="/"
    class="focus-visible:border-none focus-visible:outline-none focus-visible:ring-2 focus:ring-offset-2 focus:ring-green-500"
  >
    <Logo class="w-[15rem] min-w-[12rem]" />
  </RouterLink>
</template>

<script setup lang="ts">
import Logo from '@/components/icons/Logo.vue';
</script>
