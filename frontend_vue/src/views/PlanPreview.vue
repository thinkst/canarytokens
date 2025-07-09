<template>
  <BaseFormSelect
    id="plan-select"
    label="Select sample data"
    :options="options"
    placeholder="Choose a plan"
    @select-option="
      (value) => {
        handleSelectOption(value);
      }
    "
  />
  <GeneratePlan
    :key="selectedPlanKey"
    :initial-step-data="initialStepData"
  />
</template>

<script setup>
import { computed, ref } from 'vue';
import GeneratePlan from '@/components/tokens/aws_infra/token_setup_steps/GeneratePlan.vue';
import {
  assetsExample,
  assetsWithEmptySQSQueue,
  assetsManageExample,
  assetInitialEmptyParameter,
} from './planPreviewUtils.ts';

const selectedPlan = ref(assetsExample.value);
const selectedPlanKey = ref(0);

const initialStepData = computed(() => ({
  token: '123456789abcdef',
  auth_token: '123456789abcdef',
  code_snippet_command: 'example-command',
  proposed_plan: {
    assets: selectedPlan.value,
  },
}));

const options = [
  { label: 'Example Plan', value: assetsExample.value },
  { label: 'Unavailable SQS Queue', value: assetsWithEmptySQSQueue.value },
  {
    label: 'Empty initial SSMParameter',
    value: assetInitialEmptyParameter.value,
  },
  { label: 'Manage Plan', value: assetsManageExample.value },
];

function handleSelectOption(value) {
  console.log('Selected value:', value);
  selectedPlan.value = value;
  selectedPlanKey.value++;
}
</script>
