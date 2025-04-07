<template>
  <ul class="flex flex-row">
    <li
      v-for="(step, index) in props.steps"
      :key="step"
      class="rounded-full w-[2rem] h-[2rem] mx-24 flex justify-center items-center"
      :class="isActiveStep(index)"
    >
      <span class="text-white font-bold">{{ index + 1 }}</span>
    </li>
  </ul>
</template>

<script lang="ts" setup>
const props = defineProps<{
  steps: number;
  currentStep: number;
}>();

function isActiveStep(index: number) {
  return index + 1 <= props.currentStep ? 'bg-green-700' : 'bg-grey-200';
}
</script>
