<template>
  <div class="footer">
    <div class="lg:text-left">
      <p>
        By Using This Service, You Agree to
        <RouterLink to="/legal" class="text-green-500 hover:text-green">Our Terms of Use.</RouterLink>
      </p>
    </div>

    <div class="flex flex-col justify-center items-center">
      <div class="flex justify-center items-center text-base">
        We also build
        <!-- eslint-disable-next-line vuejs-accessibility/anchor-has-content -->
        <a href="https://canary.tools/" target="_blank">
          <LogoFooter class="w-[15rem] min-w-[12rem]" />
        </a>
      </div>
      <div v-if="BUILD_ID">
        <p>Build ID: {{ BUILD_ID }}</p>
        <p>(This will be one commit behind the frontend Dist build if you made frontend changes)</p>
      </div>
    </div>

    <div class="lg:text-right">
      <p>
        Read Our
        <base-link href="https://docs.canarytokens.org/guide/" target="_blank">Canarytokens Documentation</base-link>
      </p>
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
  @apply lg:max-w-screen-2xl sm:w-full m-auto grid items-center lg:grid-flow-row lg:grid-cols-3 lg:grid-rows-1 md:grid-flow-col md:grid-rows-3 gap-y-4 p-16 mb-24 text-xs text-center text-grey-400;
}
</style>
