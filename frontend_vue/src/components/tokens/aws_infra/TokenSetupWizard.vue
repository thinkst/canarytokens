<template>
  <BaseStepCounter
    class="mb-40"
    :steps="5"
    :current-step="currentStep"
  />
  <Suspense>
    <component
      :is="currentComponent"
      :step-data="sharedData[currentStep - 1]"
      @update-step="handleUpdateStep"
      @store-fetched-data="handleStoreFetchedData"
    />
    <template #fallblack>
      <p>Loading next step...</p>
    </template>
  </Suspense>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { defineAsyncComponent } from 'vue';
const GenerateAwsSnippet = defineAsyncComponent(
  () => import('./token_setup_steps/GenerateAwsSnippet.vue')
);
const CheckAwsPermission = defineAsyncComponent(
  () => import('./token_setup_steps/CheckAwsPermission.vue')
);
const CheckAwsRole = defineAsyncComponent(
  () => import('./token_setup_steps/CheckAwsRole.vue')
);
const InventoryAwsAccount = defineAsyncComponent(
  () => import('./token_setup_steps/InventoryAwsAccount.vue')
);
const GeneratePlan = defineAsyncComponent(
  () => import('./token_setup_steps/GeneratePlan.vue')
);
const GenerateTerraformSnippet = defineAsyncComponent(
  () => import('./token_setup_steps/GenerateTerraformSnippet.vue')
);

type GenericFetchedDataType = {
  [key: string]: string;
};

const props = defineProps<{
  tokenData: any;
}>();

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
