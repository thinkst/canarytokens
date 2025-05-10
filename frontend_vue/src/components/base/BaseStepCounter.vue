<template>
  <ol class="flex flex-row justify-center step-wrapper">
    <li
      v-for="(step, index) in props.steps"
      :key="step.label"
      class="flex"
    >
      <button
        type="button"
        class="grid grid-cols-3 group gap-y-8 md:gap-x-16 sm:gap-x-24 focus:outline-none focus-within:outline-none grid-rows-2"
        :disabled="props.currentStep <= index"
        @click="emits('handleStepClick', index + 1)"
      >
        <span
          class="step-bar step-bar__left h-[4px] mt-[1.5rem] rounded-r-sm"
          :class="isActiveStep(index) ? 'active' : 'inactive'"
          :style="`--bar-width: ${stepBarWidth}`"
        ></span>
        <span
          class="flex flex-col justify-center items-center gap-8 align-center focus:outline-none mx-8"
        >
          <!-- Circle -->
          <div
            :class="
              isActiveStep(index)
                ? 'cursor-pointer group-hover:drop-shadow-[0px_1px_1px_rgba(0,_0,_0,_0.15)] button-bg border-white drop-shadow-[0px_3px_3px_rgba(0,_0,_0,_0.25)] '
                : 'bg-grey-200 border-grey-100'
            "
            class="rounded-full w-[3rem] h-[3rem] border-[4px] border-solid flex flex-col align-center transition duration-150 ease-out group-hover:ease-in group-focus-visible:outline group-focus-visible:outline-offset-4 group-focus-visible:outline-green-300"
          >
            <span class="text-white font-bold text-xl leading-10">{{
              index + 1
            }}</span>
          </div>
        </span>
        <span
          class="step-bar step-bar__right h-[4px] mt-[1.5rem] rounded-l-sm"
          :class="isActiveStep(index + 1) ? 'active' : 'inactive'"
        ></span>
        <!-- Label -->
        <span
          class="text-sm col-span-full text-center"
          :class="
            isActiveStep(index)
              ? 'group-hover:text-green-500 text-green-500'
              : 'text-grey-400'
          "
        >
          {{ step.label }}
        </span>
      </button>
    </li>
  </ol>
</template>

<script lang="ts" setup>
import { ref, onUnmounted } from 'vue';
import { debounce } from '@/utils/utils';

type StepType = {
  label: string;
};

const props = defineProps<{
  steps: StepType[];
  currentStep: number;
}>();

const emits = defineEmits(['handleStepClick']);
const stepBarWidth = ref(50);

const handleResize = debounce(() => {
  const listRightBars = document.querySelectorAll(`.step-bar__right`);
  const firstElWidth = listRightBars[0].clientWidth;
  stepBarWidth.value = firstElWidth;
}, 300);

window.addEventListener('resize', handleResize);

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});

function isActiveStep(index: number) {
  return index + 1 <= props.currentStep;
}
</script>

<style lang="scss">
.button-bg {
  background-image: linear-gradient(
    90deg,
    hsl(147, 71%, 63%) -1.7%,
    hsl(162, 86%, 36%) 100%
  );
}

.step-wrapper {
  li:first-child {
    .step-bar {
      &__left {
        visibility: hidden;
      }
    }
  }

  li:last-child {
    .step-bar {
      &__right {
        visibility: hidden;
      }
    }
  }
}

.step-bar {
  --bar-width: 50;
  background: #cad3cf;
  background: linear-gradient(
    90deg,
    rgba(50, 195, 127, 1) 0%,
    rgba(50, 195, 127, 1) 50%,
    rgba(202, 211, 207, 1) 50%,
    rgba(202, 211, 207, 1) 100%
  );
  background-size: 200%;
  transition-property: background-position;
  transition-timing-function: ease-in-out;
  transition-duration: calc(var(--bar-width) * 2ms);

  &__left.active {
    background-position: 0%;
    transition-delay: calc(var(--bar-width) * 2ms);
  }

  &__left.inactive {
    background-position: 100%;
  }

  &__right.active {
    background-position: 0%;
  }

  &__right.inactive {
    background-position: 100%;
    transition-delay: calc(var(--bar-width) * 2ms);
  }
}
</style>
