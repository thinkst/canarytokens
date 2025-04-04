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
  () => import('./GenerateAwsSnippet.vue')
);
const CheckAwsRole = defineAsyncComponent(() => import('./CheckAwsRole.vue'));
const InventoryAwsAccount = defineAsyncComponent(
  () => import('./InventoryAwsAccount.vue')
);
const GeneratePlan = defineAsyncComponent(() => import('./GeneratePlan.vue'));
const GenerateTerraformSnippet = defineAsyncComponent(
  () => import('./GenerateTerraformSnippet.vue')
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
