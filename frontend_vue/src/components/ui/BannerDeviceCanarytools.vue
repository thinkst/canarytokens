<template>
  <div class="@container">
    <div
      class="w-full gap-16 p-16 mt-16 rounded-xl banner-bg grid @sm:justify-center @sm:items-center @sm:grid-cols-[2fr_3fr_1fr] @sm:grid-rows-[2fr] @sm:aspect-[4/1] @md:h-[180px] @sm:bg-[position:-200px_-100px,0] @sm:bg-[size:550px,cover] grid-rows-[3fr_1fr] px-16 h-[280px] aspect-[1/2] bg-[position:-250px_0px,0] bg-[size:550px,cover]"
    >
      <span class="hidden @sm:block"></span>

      <p class="@sm:self-center self-start text-xl font-light text-white">
        <span class="block mb-8 text-xs text-white">#Adv</span>
        <span class="font-bold">Did you know</span> some of the best security
        teams in the world run
        <span class="font-bold">Thinkst Canary?</span>
      </p>
      <div class="flex self-end justify-end m-w-[0px]">
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
</template>

<script lang="ts" setup></script>

<style scoped>
.banner-bg {
  background-image: url('@/assets/banner_visual.png'),
    linear-gradient(90deg, hsl(147, 71%, 63%) -1.7%, hsl(162, 86%, 36%) 100%);
  background-repeat: no-repeat;
}

@media screen and (max-width: 761px) {
  .banner-bg {
    background-image: url('@/assets/banner_visual.png'),
      linear-gradient(90deg, hsl(147, 71%, 63%) -1.7%, hsl(162, 86%, 36%) 100%);
    background-repeat: no-repeat;
  }
}
</style>
