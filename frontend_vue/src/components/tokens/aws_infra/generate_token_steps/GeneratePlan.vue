<template>
  <h2 class="step-title">Proposed Plan</h2>
  <StepState
    :is-loading="isLoading"
    :is-error="isError"
    loading-message="Loading your plan..."
    :error-message="errorMessage"
    :is-success="isSuccess"
    success-message="All set!"
  />
  <PlanCreator
    v-if="!isLoading || !isSavingPlan"
    :proposed-plan="proposed_plan"
    :token="token"
    :auth-token="auth_token"
    @submit-plan="handleSubmit"
  />
  <StepState
    :is-loading="isSavingPlan"
    :is-error="isSaveError"
    loading-message="Saving the plan..."
    :error-message="errorMessage"
    :is-success="isSaveSuccess"
    success-message="Plan Saved!"
  />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { savePlan } from '@/api/main.ts';
import PlanCreator from '@/components/tokens/aws_infra/PlanCreator.vue';
import StepState from '../StepState.vue';
import type { PlanValueTypes } from '@/components/tokens/aws_infra/types.ts';

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  stepData: any;
}>();

const isLoading = ref(true);
const isError = ref(false);
const isSuccess = ref(false);
const errorMessage = ref('');
const isSavingPlan = ref(false);
const isSaveError = ref(false);
const isSaveSuccess = ref(false);

const { token, auth_token, proposed_plan } = props.stepData;

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
    emits('storeCurrentStepData', { token, auth_token });
    emits('updateStep');
  } catch (err: any) {
    isSaveError.value = true;
    errorMessage.value = err.message;
    isSaveSuccess.value = false;
  } finally {
    isSavingPlan.value = false;
    isSaveSuccess.value = true;
  }
}

async function handleSubmit(formValues: PlanValueTypes) {
  await handleSavePlan(formValues);
}
</script>
