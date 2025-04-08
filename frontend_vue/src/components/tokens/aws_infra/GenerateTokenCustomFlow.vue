<template>
  <BaseStepCounter
    class="mb-40"
    :steps="5"
    :current-step="currentStep"
  />
  <Suspense>
    <component
      :is="currentComponent"
      v-if="!isError"
      :step-data="sharedData[currentStep - 1]"
      @update-step="handleUpdateStep"
      @store-fetched-data="handleStoreFetchedData"
    />
    <template #fallblack>
      <p>Loading next step...</p>
    </template>
  </Suspense>
  <StepState
    v-if="isError"
    :is-error="isError"
    error-message="We couldn't start the process. You'll be redirected to the Home Page."
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { defineAsyncComponent } from 'vue';
import { useRouter } from 'vue-router';
import { getTokenData } from '@/utils/dataService';
import StepState from './StepState.vue';
const GenerateAwsSnippet = defineAsyncComponent(
  () => import('./generate_token_steps/GenerateAwsSnippet.vue')
);
const CheckAwsRole = defineAsyncComponent(
  () => import('./generate_token_steps/CheckAwsRole.vue')
);
const InventoryAwsAccount = defineAsyncComponent(
  () => import('./generate_token_steps/InventoryAwsAccount.vue')
);
const GeneratePlan = defineAsyncComponent(
  () => import('./generate_token_steps/GeneratePlan.vue')
);
const GenerateTerraformSnippet = defineAsyncComponent(
  () => import('./generate_token_steps/GenerateTerraformSnippet.vue')
);

type GenericFetchedDataType = {
  [key: string]: string;
};

const router = useRouter();
const currentStep = ref(1);
const sharedData = ref(Array(5).fill({}));
const stepComponents = ref<
  Record<number, ReturnType<typeof defineAsyncComponent>>
>({
  1: GenerateAwsSnippet,
  2: CheckAwsRole,
  3: InventoryAwsAccount,
  4: GeneratePlan,
  5: GenerateTerraformSnippet,
});
const isError = ref(false);

onMounted(() => {
  sharedData.value[0] = getTokenData();
  if (sharedData.value[0] === null) {
    isError.value = true;
    setTimeout(() => {
      router.push('/');
    }, 5000);
  }
});

const currentComponent = computed(
  () => stepComponents.value[currentStep.value] || null
);

function handleUpdateStep() {
  currentStep.value++;
}

function handleStoreFetchedData(data: GenericFetchedDataType) {
  sharedData.value[currentStep.value - 1] = data;
}
</script>

<style>
.step-title {
  font-size: 2rem;
  margin-bottom: 1.5rem;
  margin-top: 1rem;
  text-align: center;
}
</style>
