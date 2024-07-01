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
    <div class="flex flex-row items-center gap-8 mt-8">
      <GithubIcon class="w-16 h-16 fill-grey-700" />
      <github-button
        href="https://github.com/thinkst/canarytokens"
        data-color-scheme="no-preference: light_high_contrast; light: light; dark: dark;"
        data-icon="octicon-star"
        data-size="large"
        data-show-count="true"
        aria-label="Star thinkst/canarytokens on GitHub"
        >Star</github-button
      >
    </div>
    <div class="flex items-center justify-center mt-24 text-xs">
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
import GithubButton from 'vue-github-button';
import GithubIcon from '@/components/icons/GithubIcon.vue';

const BUILD_ID = import.meta.env.VITE_GITHUB_SHA;
const basePath = import.meta.env.BASE_URL;
</script>
