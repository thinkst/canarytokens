<template>
  <ul class="flex flex-row place-content-evenly">
    <li
      v-for="(step, index) in props.steps"
      :key="step"
      v-tooltip="
        stepDescription
          ? {
              content: stepDescription[index],
            }
          : {}
      "
    >
      <button
        class="rounded-full w-[2rem] h-[2rem] mx-24 flex justify-center items-center"
        :class="isActiveStep(index)"
        :disabled="props.currentStep <= index"
        type="button"
        @click="emits('handleStepClick', index + 1)"
      >
        <span class="text-white font-bold">{{ index + 1 }}</span>
      </button>
    </li>
  </ul>
</template>

<script lang="ts" setup>
import { toRef } from 'vue';
const emits = defineEmits(['handleStepClick']);

const props = defineProps<{
  steps: number;
  currentStep: number;
  stepDescription?: string[];
}>();

const stepDescription = toRef(props, 'stepDescription');

function isActiveStep(index: number) {
  return index + 1 <= props.currentStep
    ? 'cursor-pointer bg-green-700  hover:bg-green-500'
    : 'bg-grey-200';
}
</script>
