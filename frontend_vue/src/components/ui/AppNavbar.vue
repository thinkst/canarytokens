<template>
  <div class="z-50 flex justify-between w-full gap-24 sm:justify-center">
    <div class="flex flex-row lg:max-w-screen-2xl sm:w-full">
      <AppLogo class="px-24 py-16" />
      <AppNavbarLinks />
    </div>
    <AppNavbarMenuMobile />
  </div>
</template>

<script setup lang="ts">
import AppLogo from './AppLogo.vue';
import AppNavbarLinks from './AppNavbarLinks.vue';
import AppNavbarMenuMobile from './AppNavbarMenuMobile.vue';
</script>
