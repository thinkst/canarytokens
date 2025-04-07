<template>
  <div class="infra-token__title-wrapper">
    <h2>Proposed Plan</h2>
  </div>
  <div class="flex items-center flex-col">
    <StepState
      :is-loading="isLoading"
      :is-error="isError"
      loading-message="Loading your plan..."
      :error-message="errorMessage"
    />
    <p>This is a placeholder for the plan</p>
    <p>The Plan editor is WIP on another branch</p>
    <p>Just hit save to check the next step</p>
    <br />
    <BaseButton @click="handleSubmit(proposed_plan)">Save Plan</BaseButton>
    <StepState
      :is-loading="isSavingPlan"
      :is-error="isSaveError"
      loading-message="Saving the plan..."
      :error-message="errorMessage"
      :is-success="isSaveSuccess"
      success-message="Plan Saved!"
    />
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { savePlan } from '@/api/awsInfra.ts';
import StepState from '../StepState.vue';
import type { TokenDataType } from '@/utils/dataService';
import type { PlanValueTypes } from '@/components/tokens/aws_infra/types.ts';

const emits = defineEmits(['updateStep', 'storeFetchedData']);

const props = defineProps<{
  initialStepData: TokenDataType;
}>();

const isLoading = ref(true);
const isError = ref(false);
const errorMessage = ref('');
const isSavingPlan = ref(false);
const isSaveError = ref(false);
const isSaveSuccess = ref(false);

const { token, auth_token, proposed_plan } = props.initialStepData;

isLoading.value = false;

async function handleSavePlan(formValues: PlanValueTypes) {
  isSavingPlan.value = true;
  isSaveError.value = false;
  isSaveSuccess.value = false;

  try {
    const res = await savePlan(token, auth_token, formValues);
    if (res.status !== 200) {
      isSavingPlan.value = false;
      isSaveError.value = true;
      errorMessage.value = res.data.message;
    }
    isSaveSuccess.value = true;
    emits('storeCurrentStepData', { token, auth_token });
    emits('updateStep');
  } catch (err: any) {
    isSaveError.value = true;
    errorMessage.value = err.message;
    isSaveSuccess.value = false;
  } finally {
    isSavingPlan.value = false;
  }
}

async function handleSubmit(formValues: PlanValueTypes) {
  await handleSavePlan(formValues);
}
</script>
