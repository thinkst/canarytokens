<template>
  <div class="flex flex-col items-center justify-center align-middle">
    <h2 class="text-xl text-grey-500">
      We're sorry, but we couldn't find the token you're looking for.
    </h2>
    <img
      :src="getImageUrl('icons/404Icon.svg')"
      alt="Token not found"
      class="w-[50%] max-w-[200px] my-32 not-sr-only"
    />
    <p class="text-center text-grey-400">
      This could be because the
      <span class="font-semibold">authentication</span> or
      <span class="font-semibold">token</span> provided is incorrect.
    </p>
    <p class="text-center text-grey-400">
      Please check your token details and try again.
    </p>
  </div>
</template>

<script setup lang="ts">
import getImageUrl from '@/utils/getImageUrl';
</script>
