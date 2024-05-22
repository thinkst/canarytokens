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
import AppNavbar from '@/components/ui/AppNavbar.vue';
import AppFooter from '@/components/ui/AppFooter.vue';
import AppLayout from '@/layout/AppLayout.vue';
import { ModalsContainer } from 'vue-final-modal';
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}
</style>
