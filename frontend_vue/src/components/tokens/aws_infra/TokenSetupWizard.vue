<template>
  <BaseStepCounter
    :steps="5"
    :current-step="currentStep"
  />
  <component
    :is="currentComponent"
    @update-step="handleUpdateStep"
  />
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

const currentStep = ref(1);

const stepComponents = {
  1: GenerateAwsSnippet,
  2: CheckAwsRole,
  3: InventoryAwsAccount,
  4: GeneratePlan,
  5: GenerateTerraformSnippet,
};

const currentComponent = computed(
  () => stepComponents[currentStep.value] || null
);

function handleUpdateStep() {
  currentStep.value++;
}
</script>
