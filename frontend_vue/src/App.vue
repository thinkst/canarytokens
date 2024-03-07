<template>
  <header>
      <AppNavbar />
  </header>
    <LayoutMain>
      <RouterView/>
    </LayoutMain>
  <footer>
      <AppFooter />
  </footer>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router';
import AppNavbar from '@/components/AppNavbar.vue';
import AppFooter from '@/components/AppFooter.vue';
import LayoutMain from '@/layout/LayoutMain.vue';


</script>


<style scoped>


</style>
