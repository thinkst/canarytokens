<template>
  <h2 class="step-title">
    {{ isLoading || isError ? 'Checking Role...' : 'Role Checked!' }}
  </h2>
  <StepState
    :is-loading="isLoading"
    :is-error="isError"
    loading-message="We are checking the role, hold on"
    :error-message="errorMessage"
    :is-success="isSuccess"
    success-message="All set!"
  />

  <p v-if="isSuccess">On the next step you'll be inventoring your account</p>
  <BaseButton
    v-if="isSuccess"
    class="mt-40"
    @click="emits('updateStep')"
  >
    Continue to inventory</BaseButton
  >
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import type { tokenDataType } from '@/utils/dataService';
import { getAWSinfraCheckRole } from '@/api/main.ts';
import StepState from '../StepState.vue';

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  stepData: tokenDataType;
}>();

const isLoading = ref(true);
const isError = ref(false);
const isSuccess = ref(false);
const errorMessage = ref('');

const { token, auth_token } = props.stepData;

onMounted(async () => {
  await handleCheckRole();
});

async function handleCheckRole() {
  isLoading.value = true;
  isError.value = false;
  isSuccess.value = false;

  try {
    const res = await getAWSinfraCheckRole(token, auth_token, null);
    if (res.status !== 200) {
      isLoading.value = false;
      isError.value = true;
      errorMessage.value = res.data.error_message;
    }
    console.log(res.data, 'res one!');

    const handle = res.data.handle;

    const resWithHandle = await getAWSinfraCheckRole(token, auth_token, handle);
    if (resWithHandle.status !== 200) {
      isLoading.value = false;
      isError.value = true;
      errorMessage.value = resWithHandle.data.error_message;
    }
    // console.log(JSON.parse(resWithHandle.data), 'json!');
    console.log(resWithHandle.data, 'resWithHandle!');
    emits('storeCurrentStepData', { token, auth_token });
  } catch (err: any) {
    isError.value = true;
    errorMessage.value = err;
  } finally {
    isLoading.value = false;
    isSuccess.value = true;
  }
}
</script>
