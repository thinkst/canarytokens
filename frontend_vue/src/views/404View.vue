<template>
  <div class="flex flex-col items-center justify-center align-middle">
    <h2 class="text-xl text-grey-500">
      Oops! The page you're looking for can't be found.
    </h2>
    <img
      :src="getImageUrl('token_icons/default.png')"
      alt="Page Not Found"
      class="w-[50%] max-w-[200px] my-32 not-sr-only"
    />
    <p class="text-center text-grey-400">
      This might be because the URL is incorrect, or the page has been moved or
      deleted.
    </p>
    <p class="text-center text-grey-400">
      Please check the URL or go back to the homepage and try again.
    </p>
  </div>
</template>

<script setup lang="ts">
import getImageUrl from '@/utils/getImageUrl';
</script>
