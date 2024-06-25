<template>
  <div class="flex flex-col items-center w-full">
    <div class="footer">
      <div class="order-1 lg:text-left">
        <p>
          By Using This Service, You Agree to
          <RouterLink
            to="/legal"
            class="text-green-500 hover:text-green"
            >Our Terms of Use.</RouterLink
          >
        </p>
      </div>

      <div class="flex flex-col items-center justify-center order-3 lg:order-3">
        <div class="flex items-center justify-center text-base">
          We also build
          <!-- eslint-disable-next-line vuejs-accessibility/anchor-has-content -->
          <a
            href="https://canary.tools/"
            target="_blank"
          >
            <LogoFooter class="w-[15rem] min-w-[12rem]" />
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

      <div class="order-2 lg:text-right lg:order-3">
        <p>
          Read Our
          <base-link
            href="https://docs.canarytokens.org/guide/"
            target="_blank"
            >Canarytokens Documentation</base-link
          >
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
import LogoFooter from '@/components/icons/LogoFooter.vue';

const BUILD_ID = import.meta.env.VITE_GITHUB_SHA;
</script>

<style scoped>
.footer {
  @apply lg:max-w-screen-2xl w-full flex items-center flex-col lg:flex-row justify-center lg:justify-between gap-4 lg:gap-40 mb-24 mx-16 px-40 text-xs text-center text-grey-400;
}
</style>
