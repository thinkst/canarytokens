<template>
  <button
    class="focus-visible:border-none focus-visible:outline-none focus-visible:ring-2 focus:ring-offset-2 focus:ring-green-500"
    type="button"
    @click="handleLinkClick('/')"
  >
    <span class="sr-only">Home</span>
    <LogoNavbar class="w-[15rem] min-w-[12rem]" />
  </button>
</template>

<script setup lang="ts">
import LogoNavbar from '@/components/icons/LogoNavbar.vue';
import { useRouter } from 'vue-router';
import { addViewTransition } from '@/utils/utils';

const router = useRouter();

function handleLinkClick(path: string) {
  //@ts-ignore
  addViewTransition(() => router.push(path));
  document.getElementById('clearSearchInput')?.click();
}
</script>
