<template>
  <div
    class="grid items-center grid-cols-1 px-24 py-16 mb-16 text-xs text-center text-grey-400"
  >
    <div class="flex justify-center py-16">
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
      <div v-if="BUILD_ID">
        <p>Build ID: {{ BUILD_ID }}</p>
        <p>(This will be one commit behind the frontend Dist build if you made frontend changes)</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';

const BUILD_ID = import.meta.env.VITE_GITHUB_SHA;
</script>
