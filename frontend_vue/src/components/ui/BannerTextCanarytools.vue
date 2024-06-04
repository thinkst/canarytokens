<template>
  <div
    class="grid sm:grid-cols-[1fr_5fr] border gap-32 border-grey-200 items-center p-32 bg-white rounded-xl shadow-solid-shadow-grey-sm"
  >
    <div class="justify-center hidden sm:flex">
      <img
        :src="getImageUrl(`thinkst_canary_logo.png`)"
        alt="logo Canarytokens"
        class="w-full sm:block max-w-[8rem]"
      />
    </div>
    <div class="text-left">
      <p class="text-xl font-semibold leading-normal text-grey-800">
        We hope you enjoy the free version of Canarytokens!
      </p>
      <p class="mt-16 leading-relaxed text-balance text-grey-500">
        For more (non-public) tokens, support, mass-deployment-tools and better
        management of your deployed tokens, check out our commercial offering at
        <base-link
          class="font-semibold"
          href="https://canary.tools"
          target="_blank"
          >https://canary.tools</base-link
        >
      </p>
    </div>
  </div>
</template>

<script lang="ts" setup>
import getImageUrl from '@/utils/getImageUrl';
</script>
