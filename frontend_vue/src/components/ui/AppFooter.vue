<template>
  <div
    class="text-grey-400 h-[100px] px-24 py-16 text-xs text-center grid grid-cols-1 lg:grid-cols-3 items-center"
  >
    <div class="flex justify-center py-16 lg:py-0 lg:justify-start">
      <a
        href="https://canary.tools/"
        target="_blank"
        ><img
          src="@/assets/logo_footer.svg"
          alt="logo"
      /></a>
    </div>
    <div>
      <p>
        Read Our
        <base-link
          href="https://docs.canarytokens.org/guide/"
          target="_blank"
          >Canarytokens Documentation</base-link
        >
      </p>
      <p>
        By Using This Service, You Agree to
        <RouterLink
          to="/legal"
          class="text-green-500 hover:text-green"
          >Our Terms of Use.</RouterLink
        >
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
</script>
