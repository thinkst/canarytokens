<template>
  <button
    v-tooltip="{
      content: tooltipText,
      shown: isTriggered,
      triggers: tooltipTriggers,
    }"
    class="refresh-token h-[2rem] w-[2rem] font-semibold rounded-full bg-white hover:bg-green-50 hover:text-green-500 focus:text-green-500 focus-visible:outline-0 focus:bg-green-100 focus:border-green-200 focus:outline-0 text-green-600 border border-green-200"
    aria-label="Refresh token"
    @click="handleRefreshToken"
  >
    <Transition
      name="fade"
      mode="out-in"
    >
      <font-awesome-icon
        v-if="!isTriggered"
        aria-hidden="true"
        icon="rotate-right"
      ></font-awesome-icon>
      <font-awesome-icon
        v-else
        aria-hidden="true"
        icon="check"
      ></font-awesome-icon
    ></Transition>
    <span
      v-if="isTriggered"
      class="fa-sr-only"
      >Token Refreshed</span
    >
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const emits = defineEmits(['refresh-token']);

const tooltipText = ref('Refresh token');
const isTriggered = ref(false);
const tooltipTriggers = ref(['hover', 'focus']);

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function showTooltip() {
  await delay(150);
  tooltipTriggers.value = [];
  isTriggered.value = true;
  tooltipText.value = 'Refreshed!';
  // vTooltip sets a default delay of 1.5s
  await delay(1500);
  isTriggered.value = false;
  tooltipTriggers.value = ['hover', 'focus'];
  await delay(150);
  tooltipText.value = 'Refresh token';
}

function handleRefreshToken() {
  showTooltip();
  emits('refresh-token');
}
</script>

<style scoped>
@keyframes bounce {
  40% {
    transform: scale(1.2);
  }
  80% {
    transform: scale(0.8);
  }
  100% {
    transform: scale(1);
  }
}

.fade-enter-active,
.fade-leave-active {
  animation: bounce 350ms;
}
.fade-enter,
.fade-leave-to {
  transform: scale(1);
}
</style>
