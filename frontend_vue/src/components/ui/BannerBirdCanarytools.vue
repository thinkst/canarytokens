<template>
  <div class="flex justify-center w-full mt-24 md:px-32">
    <div
      class="flex px-8 pt-16 sm:px-16 justify-centergap-16 lg:px-32 banner-bg rounded-2xl"
    >
      <img
        :src="getImageUrl('inyoni.gif')"
        alt="bird_canarytools"
        class="sm:w-[5rem] translate-y-[-1rem] flex-shrink-1 aspect-auto h-[6rem] self-center"
      />
      <div class="px-16 py-8 sm:px-8">
        <p class="@sm:self-center self-start text-xl font-light text-white">
          <span class="block mb-8 text-xs text-white">#Adv</span>
          <span class="font-bold">Did you know</span> some of the best security
          teams in the world run
          <span class="font-bold">Thinkst Canary?</span>
        </p>
        <div class="flex self-end justify-end mt-8">
          <BaseButton
            class="whitespace-nowrap"
            variant="text-light"
            icon-position="right"
            icon="arrow-right"
            href="https://canary.tools/"
            target="_blank"
            >Find out</BaseButton
          >
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import getImageUrl from '@/utils/getImageUrl';
</script>

<style scoped>
.banner-bg {
  background-image: linear-gradient(
    45deg,
    hsl(147, 71%, 63%) -1.7%,
    hsl(162, 86%, 36%) 100%
  );
}
</style>
