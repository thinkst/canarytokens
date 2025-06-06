<template>
  <section class="w-full flex text-center flex-col items-center">
    <div class="infra-token__title-wrapper">
      <h2>
        {{ isLoading || isError ? 'Checking Role...' : 'Role Checked!' }}
      </h2>
    </div>
    <StepState
      :is-loading="isLoading"
      :is-error="isError"
      loading-message="We are checking the role, hold on"
      :error-message="errorMessage"
      :is-success="isSuccess"
      success-message="All set!"
    />
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
import type { TokenDataType } from '@/utils/dataService';
import { requestAWSInfraRoleCheck } from '@/api/awsInfra.ts';
import StepState from '../StepState.vue';
import {StepStateEnum, useStepState} from '@/components/tokens/aws_infra/useStepState.ts';

const emits = defineEmits([
  'updateStep',
  'storeCurrentStepData',
  'isSettingError',
]);

const props = defineProps<{
  initialStepData: TokenDataType;
}>();

const stateStatus = ref<StepStateEnum>(StepStateEnum.LOADING);
const errorMessage = ref('');
const { isLoading, isError, isSuccess } = useStepState(stateStatus);

const { token, auth_token } = props.initialStepData;

onMounted(async () => {
  emits('isSettingError', false);
  await handleCheckRole();
});

async function handleCheckRole() {
  const POLL_INTERVAL = 2000;
  errorMessage.value = '';
  stateStatus.value = StepStateEnum.LOADING;

  try {
    const res = await requestAWSInfraRoleCheck({
      canarytoken: token,
      auth_token,
    });
    if (res.status !== 200) {
      stateStatus.value = StepStateEnum.ERROR;
      errorMessage.value = res.data.message;
      emits('isSettingError', true);
    }

    const handle = res.data.handle;

    const startTime = Date.now();
    const timeout = 5 * 60 * 1000;

    const pollInfraRoleCheck = async () => {
      try {
        const resWithHandle = await requestAWSInfraRoleCheck({ handle });

        if (resWithHandle.status !== 200) {
          stateStatus.value = StepStateEnum.ERROR;
          errorMessage.value = resWithHandle.data.error;
          emits('isSettingError', true);
          clearInterval(pollingRoleInterval);
          return;
        }

        if (resWithHandle.data.error) {
          stateStatus.value = StepStateEnum.ERROR;
          errorMessage.value = resWithHandle.data.error;
          emits('isSettingError', true);
          clearInterval(pollingRoleInterval);
          return;
        }

        // timeout
        if (Date.now() - startTime >= timeout) {
          stateStatus.value = StepStateEnum.ERROR;
          errorMessage.value = 'The operation took too long. Try again.';
          emits('isSettingError', true);
          clearInterval(pollingRoleInterval);
          return;
        }

        // success
        if (resWithHandle.data.session_credentials_retrieved) {
          stateStatus.value = StepStateEnum.SUCCESS;
          emits('storeCurrentStepData', { token, auth_token });
          clearInterval(pollingRoleInterval);
          emits('updateStep');
          return;
        }
      } catch (err: any) {
        stateStatus.value = StepStateEnum.ERROR;
        errorMessage.value =
          err.message || 'An error occurred while checking the Role. Try again';
        emits('isSettingError', true);
        clearInterval(pollingRoleInterval);
        return;
      }
    };

    const pollingRoleInterval = setInterval(pollInfraRoleCheck, POLL_INTERVAL);
  } catch (err: any) {
    stateStatus.value = StepStateEnum.ERROR;
    errorMessage.value = err.message;
    emits('isSettingError', true);
  }
}
</script>
