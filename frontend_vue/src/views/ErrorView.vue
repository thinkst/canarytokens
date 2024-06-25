<template>
  <div
    class="flex flex-col items-center justify-center flex-grow h-auto px-16 text-center"
  >
    <h2 class="text-xl text-grey-500">
      {{ header }}
    </h2>
    <img
      :src="getImageUrl('icons/errorIcon.svg')"
      alt="Page Not Found"
      class="w-[50%] max-w-[200px] my-32 not-sr-only"
    />
    <p class="text-center text-grey-400">
      {{ description }}
    </p>
    <p class="text-center text-grey-400">
      {{ action }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import getImageUrl from '@/utils/getImageUrl';
import { useRoute } from 'vue-router';

const route = useRoute();
const header = computed(() => route.meta.header);
const description = computed(() => route.meta.description);
const action = computed(() => route.meta.action);
</script>
