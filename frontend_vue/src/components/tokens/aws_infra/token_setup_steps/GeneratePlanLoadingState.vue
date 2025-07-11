<template>
  <div class="my-16 flex flex-col items-center mt-24">
    <p class="mb-24">
      This will take a couple of seconds for us to analyse your account,
      depending on network conditions, solar flare activity, and errant
      squirrels. Hold on…
    </p>
    <ul class="flex-row flex gap-24 checks-list">
      <li
        v-for="(value, i) in instructions"
        :key="i"
        class="flex items-center mb-4 gap-8"
      >
        <span
          class="w-[1.5rem] h-[1.5rem] bg-green-500 rounded-full flex items-center justify-center"
        >
          <font-awesome-icon
            icon="check"
            class="text-white"
          />
        </span>
        <span class="text-left leading-5">{{ value }}</span>
      </li>
    </ul>
    <img
      :src="getImageUrl('aws_infra_token_loading_scanner.gif')"
      alt="Loading"
      class="w-[15rem] h-[15rem] mt-40"
    />
    <p class="mt-40">Please, don't close this window</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import getImageUrl from '@/utils/getImageUrl';

const instructions = ref([
  'AWS account found',
  'Verifying setup',
  'Analysing cloud account',
]);
</script>

<style lang="scss" scoped>
@keyframes add-color {
  from {
    filter: grayscale(100%);
  }
  to {
    filter: grayscale(0%);
    opacity: 1;
  }
}

.checks-list {
  li {
    filter: grayscale(100%);
    opacity: 0.4;

    @for $i from 1 through 3 {
      &:nth-child(#{$i}) {
        animation: add-color 0.5s ease-in-out forwards;
        animation-delay: #{($i) * 1s};
      }
    }
  }
}
</style>
