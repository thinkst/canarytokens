<template>
  <section class="w-full flex text-center flex-col items-center">
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
    <BaseButton
      v-if="isError"
      class="mt-40"
      variant="secondary"
      @click="handleCheckRole"
    >
      Try again
    </BaseButton>
  </section>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import type { tokenDataType } from '@/utils/dataService';
import { requestAWSInfraRoleCheck } from '@/api/main.ts';
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
    const res = await requestAWSInfraRoleCheck({
      canarytoken: token,
      auth_token,
    });
    if (res.status !== 200) {
      isLoading.value = false;
      isError.value = true;
      errorMessage.value = res.data.error_message;
    }

    const handle = res.data.handle;

    // mocked result
    const resWithHandle = {
      data: {
        result: true,
        session_credentials_retrieved: true,
        error: ''
      }
    }
    // const resWithHandle = await requestAWSInfraRoleCheck({
    //   handle,
    // });

    if (
      !resWithHandle.data.result &&
      !resWithHandle.data.session_credentials_retrieved
    ) {
      isLoading.value = false;
      isError.value = true;
      errorMessage.value = resWithHandle.data.error;
    }

    isSuccess.value = true;
    emits('storeCurrentStepData', { token, auth_token });
  } catch (err: any) {
    isError.value = true;
    errorMessage.value = err.message;
    isSuccess.value = false;
  } finally {
    isLoading.value = false;
  }
}

</script>
