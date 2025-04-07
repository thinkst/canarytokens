<template>
  <h2 class="step-title">Role checked!</h2>
  <div v-if="isLoading">Loading...</div>

  <p>On the next step you'll be inventoring your account</p>
  <font-awesome-icon
    icon="circle-check"
    aria-hidden="true"
    class="text-green w-[6rem] h-[6rem] mt-24"
  />
  <BaseButton
    v-if="!isLoading"
    class="mt-40"
    @click="emits('updateStep')"
  >
    Continue to inventory</BaseButton
  >
</template>

<script lang="ts" setup>
import { ref } from 'vue';

const emits = defineEmits(['updateStep', 'storeFetchedData']);

const props = defineProps<{
  stepData: any;
}>();

const isLoading = ref(false);
</script>
