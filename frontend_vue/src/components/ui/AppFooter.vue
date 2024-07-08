<template>
  <div
    class="flex flex-col items-center justify-center w-full mb-24 text-xs text-center text-grey-400"
  >
    <p>
      By Using This Service, You Agree to
      <base-link
        :href="`${basePath}/legal`"
        target="_blank"
        >Our Terms of Use.</base-link
      >
    </p>
    <p>
      Read Our
      <base-link
        href="https://docs.canarytokens.org/guide/"
        target="_blank"
        >Canarytokens Documentation</base-link
      >
    </p>
    <div class="flex items-center justify-center mt-8 text-xs">
      We also build
      <a
        href="https://canary.tools/"
        target="_blank"
      >
        <LogoFooter class="min-w-[12rem]" />
        <a
          href="https://canary.tools/"
          target="_blank"
          class="sr-only"
        >
          Canary tools
        </a>
      </a>
    </div>
    <div
      v-if="BUILD_ID"
      class="mt-8"
    >
      <p>Build ID: {{ BUILD_ID }}</p>
      <p>
        (This will be one commit behind the frontend Dist build if you made
        frontend changes)
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import LogoFooter from '@/components/icons/LogoFooter.vue';

const BUILD_ID = import.meta.env.VITE_GITHUB_SHA;
const basePath = import.meta.env.BASE_URL;
</script>
