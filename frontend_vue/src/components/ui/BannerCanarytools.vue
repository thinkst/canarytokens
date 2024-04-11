<template>
  <div class="w-full mt-16 rounded-xl banner">
    <p>
      <span class="font-bold">Did you know</span> some of the best security
      teams in the world run
      <span class="font-bold">Thinkst Canary?</span>
    </p>
  </div>
</template>

<script lang="ts" setup></script>

<style scoped>
.banner {
  aspect-ratio: 4 / 1;
  max-height: 200px;
  background-image: url('@/assets/banner_visual.png'),
    linear-gradient(90deg, #33c481 -1.7%, #53dfbd 100%);
  background-position: -50% 30%;
  background-size: 30vw, cover;
  background-repeat: no-repeat;
}

@media screen and (max-width: 761px) {
  .banner {
    aspect-ratio: 1 / 2;
    max-height: 280px;
    background-image: url(/newuiwhodis/src/assets/banner_visual.png),
      linear-gradient(90deg, #33c481 -1.7%, #53dfbd 100%);
    background-position:
      -15vh 5vh,
      0;
    background-size: 100vw, cover;
    background-repeat: no-repeat;
  }
}
</style>
