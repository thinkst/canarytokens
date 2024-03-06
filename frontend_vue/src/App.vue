<template>
  <header>
      <AppNavbar />
  </header>
  <main class="bg-grey-50 main-height">
      <RouterView/>
  </main>
  <footer>
      <AppFooter />
  </footer>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router';
import AppNavbar from '@/components/AppNavbar.vue';
import AppFooter from '@/components/AppFooter.vue';

</script>


<style scoped>

.main-height {
  min-height: calc(100svh - (100px + 100px));
}

</style>
