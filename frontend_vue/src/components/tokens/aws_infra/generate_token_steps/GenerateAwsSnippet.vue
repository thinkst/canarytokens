<template>
  <h2 class="step-title">Generate Snippet</h2>
  <h3 class="max-w-[60%] min-w-[350px]">
    We require you to create a role in your account so that we can inventory
    resources and suggest a plan for you
  </h3>
  <div v-if="isLoading">Loading...</div>
  <div v-else>
    <BaseCodeSnippet
      lang="bash"
      label="Run this command in your terminal"
      :code="placeholderCode"
      class="mt-40"
    ></BaseCodeSnippet>
  </div>
  <BaseButton
    v-if="!isLoading"
    class="mt-40"
    @click="emits('updateStep')"
  >
    Done, proceed</BaseButton
  >
</template>

<script lang="ts" setup>
import { ref } from 'vue';

const emits = defineEmits(['updateStep', 'storeFetchedData']);

// const props = defineProps<{
//   stepData: any;
// }>();

const isLoading = ref(false);
const placeholderCode = 'echo "This is a placeholder command "';
</script>

<style scoped></style>
