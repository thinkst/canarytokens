<template>
  <div
    :class="[
      props.hasShadow ? 'token-icon-shadow' : '',
      props.isInteracted ? 'token-icon-interacted' : '',
      props.hasAnimation ? 'token-icon-animated' : '',
    ]"
  >
    <BaseSkeletonLoader
      v-if="isLoading"
      type="circle"
      class="ratio-[1:1] w-full h-full"
    />
    <img
      v-if="!isLoading"
      :src="src"
      class="transition-transform duration-200"
      :class="[
        props.isInteracted ? 'translate-y-[-0.2rem]' : '',
        props.hasAnimation ? 'animate-float' : '',
      ]"
      aria-hidden="true"
      :alt="`${title} logo`"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, toRef } from 'vue';
import getImageUrl from '@/utils/getImageUrl';

const props = withDefaults(
  defineProps<{
    title: string;
    logoImgUrl: string;
    isInteracted?: boolean;
    hasAnimation?: boolean;
    hasShadow?: boolean;
  }>(),
  {
    logoImgUrl: 'default.png',
    hasShadow: true,
  }
);

const logoUrl = toRef(props, 'logoImgUrl');
const isLoading = ref(true);
const src = ref('');

onMounted(() => {
  loadImage();
});

async function loadImage() {
  src.value = '';
  isLoading.value = true;
  const img = new Image();
  const tokenLogoUrl = getImageUrl(`token_icons/${logoUrl.value}`);
  img.src = tokenLogoUrl;
  await new Promise((resolve) => (img.onload = resolve));
  src.value = img.src;
  isLoading.value = false;
}

watch(logoUrl, () => {
  loadImage();
});
</script>

<style scoped>
/* Add shadow */
.token-icon-shadow::after {
  content: '';
  position: absolute;
  display: inline-block;
  left: 50%;
  width: 3rem;
  height: 0.5rem;
  border-radius: 50%;
  @apply bg-grey-100;
  filter: blur(0.1rem);
  transform: translate(-50%, 0.2rem);
}

.token-icon-interacted::after {
  width: 2.8rem;
}

@keyframes shadow-pulse {
  0%,
  100% {
    width: 3rem;
  }
  50% {
    width: 2.5rem;
  }
}

.token-icon-animated::after {
  animation: shadow-pulse 2s infinite;
}

/* Add animation */
@keyframes float {
  0%,
  100% {
    transform: translateY(0);
    animation-timing-function: cubic-bezier(0.645, 0.045, 0.355, 1);
  }
  50% {
    transform: translateY(-0.3rem);
    animation-timing-function: cubic-bezier(0.645, 0.045, 0.355, 1);
  }
}

.animate-float {
  animation: float 2s ease-in-out infinite;
}
</style>
