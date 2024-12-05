<template>
  <div
    :class="props.disabled ? 'hover:brightness-100' : 'hover:brightness-110'"
    class="relative flex items-center justify-center p-8 duration-100 bg-white border cursor-pointer rounded-2xl border-grey-200"
  >
    <a
      v-bind="$attrs"
      class="bg-cover min-w-[4rem] min-h-[4rem] rounded-2xl duration-100"
      :class="{ 'bg-grey-200 cursor-default': props.disabled }"
      :style="
        !props.disabled && props.url
          ? { backgroundImage: `url(${props.url})` }
          : ''
      "
      :disabled="props.disabled"
      download
      :href="props.url"
      @click="downloadContent"
    >
      <span class="sr-only">{{ props.alt }} Download</span>

      <span
        v-tooltip="{
          content: tooltipText,
          shown: isTriggered,
          triggers: tooltipTriggers,
        }"
        :class="{ hidden: props.disabled }"
        class="absolute w-[2rem] rounded-full h-[2rem] bg-green top-[-.5rem] right-[-.5rem] flex items-center justify-center text-white"
      >
        <Transition
          name="fade"
          mode="out-in"
        >
          <font-awesome-icon
            v-if="!isTriggered"
            icon="arrow-down"
          ></font-awesome-icon>
          <font-awesome-icon
            v-else
            aria-hidden="true"
            icon="check"
          ></font-awesome-icon>
        </Transition>
      </span>
    </a>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';

const props = defineProps<{
  url?: string;
  alt?: string;
  disabled?: boolean;
}>();

const tooltipText = ref('Download');
const isTriggered = ref(false);
const tooltipTriggers = ref(['hover', 'focus']);

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// 1. prevents UI from jumping when tooltip content changes
// 2. shows tooltip when content is downloaded
async function showTooltip() {
  await delay(150);
  tooltipTriggers.value = [];
  isTriggered.value = true;
  tooltipText.value = 'Download started!';
  // vTooltip sets a default delay of 1.5s
  await delay(1500);
  isTriggered.value = false;
  tooltipTriggers.value = ['hover', 'focus'];
  await delay(150);
  tooltipText.value = 'Download';
}

function downloadContent() {
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
