<template>
  <div class="flex flex-col justify-between min-h-screen">
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
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import AppNavbar from '@/components/ui/AppNavbar.vue';
import AppFooter from '@/components/ui/AppFooter.vue';
import AppLayout from '@/layout/AppLayout.vue';
import { ModalsContainer } from 'vue-final-modal';
</script>
