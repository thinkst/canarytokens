<template>
  <ModalsContainer />
  <header>
    <AppNavbar />
  </header>
  <AppLayout>
    <RouterView />
  </AppLayout>
  <footer>
    <AppFooter />
  </footer>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import AppNavbar from '@/components/AppNavbar.vue';
import AppFooter from '@/components/AppFooter.vue';
import AppLayout from '@/layout/AppLayout.vue';
import { ModalsContainer } from 'vue-final-modal'

</script>


<style scoped></style>
