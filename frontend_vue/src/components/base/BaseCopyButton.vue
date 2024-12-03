<template>
  <button
    v-tooltip="{
      content: tooltipText,
      shown: isTriggered,
      triggers: tooltipTriggers,
    }"
    class="h-[2rem] w-[2rem] font-semibold text-white rounded-full bg-green hover:bg-green-300 transition duration-100"
    aria-label="Copy to clipboard"
    @click="copyContent"
  >
    <Transition
      name="fade"
      mode="out-in"
    >
      <font-awesome-icon
        v-if="!copied"
        aria-hidden="true"
        icon="copy"
      ></font-awesome-icon>
      <font-awesome-icon
        v-else
        aria-hidden="true"
        icon="check"
      ></font-awesome-icon
    ></Transition>
    <span
      v-if="copied"
      class="fa-sr-only"
      >Copied content</span
    >
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useClipboard } from '@vueuse/core';

const props = withDefaults(
  defineProps<{
    content: string;
  }>(),
  {
    content: '',
  }
);

const { isSupported, copy, copied } = useClipboard({
  //@ts-ignore
  content: props.content,
});

const tooltipText = ref('Copy to clipboard');
const isTriggered = ref(false);
const tooltipTriggers = ref(['hover', 'focus']);

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// 1. prevents UI from jumping when tooltip content changes
// 2. shows tooltip when content is copied
async function showTooltip() {
  if (!isSupported || !navigator.clipboard) return (tooltipText.value = 'Copy not supported');
  await delay(150);
  tooltipTriggers.value = [];
  isTriggered.value = true;
  tooltipText.value = 'Copied!';
  // vTooltip sets a default delay of 1.5s
  await delay(1500);
  isTriggered.value = false;
  tooltipTriggers.value = ['hover', 'focus'];
  await delay(150);
  tooltipText.value = 'Copy to clipboard';
}

function copyContent() {
  copy(props.content);
  showTooltip();
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
