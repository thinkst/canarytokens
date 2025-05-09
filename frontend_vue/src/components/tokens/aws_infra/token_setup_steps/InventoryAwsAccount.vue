<template>
  <section class="w-full flex text-center flex-col items-center">
    <div class="infra-token__title-wrapper">
      <h2>
        {{ isLoading || isError ? 'Inventoring...' : 'Inventory done!' }}
      </h2>
    </div>
    <StepState
      :is-loading="isLoading"
      :is-error="isError"
      loading-message="We are inventoring your account, hold on"
      :error-message="errorMessage"
      :is-success="isSuccess"
      success-message="All set!"
    />
  </section>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { requestInventoryCustomerAccount } from '@/api/awsInfra.ts';
import type { TokenDataType } from '@/utils/dataService';
import { useCountdown } from '@/utils/useCountdown';
import StepState from '../StepState.vue';
import {
  StepStateEnum,
  useStepState,
} from '@/components/tokens/aws_infra/useStepState.ts';

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  initialStepData: TokenDataType;
}>();

const stateStatus = ref<StepStateEnum>(StepStateEnum.LOADING);
const errorMessage = ref('');
const { isLoading, isError, isSuccess } = useStepState(stateStatus);

const { token, auth_token } = props.initialStepData;

onMounted(async () => {
  await handleInventory();
});

async function handleInventory() {
  const POLL_INTERVAL = 2000;
  errorMessage.value = '';
  stateStatus.value = StepStateEnum.LOADING;

  try {
    const res = await requestInventoryCustomerAccount({
      canarytoken: token,
      auth_token,
    });

    if (res.status !== 200) {
      stateStatus.value = StepStateEnum.ERROR;
      errorMessage.value = res.data.error_message;
    }

    const handle = res.data.handle;

    const startTime = Date.now();
    const timeout = 5 * 60 * 1000; // 5 minutes

    const pollInventoryCustomerAccount = async () => {
      try {
        const resWithHandle = await requestInventoryCustomerAccount({ handle });

        if (resWithHandle.status !== 200) {
          stateStatus.value = StepStateEnum.ERROR;
          errorMessage.value = resWithHandle.data.error;
          clearInterval(pollingInventoringInterval);
          return;
        }

        if (resWithHandle.data.error) {
          stateStatus.value = StepStateEnum.ERROR;
          errorMessage.value = resWithHandle.data.error;
          clearInterval(pollingInventoringInterval);
          return;
        }

        // timeout
        if (Date.now() - startTime >= timeout) {
          stateStatus.value = StepStateEnum.ERROR;
          errorMessage.value = 'The operation took too long. Try again.';
          clearInterval(pollingInventoringInterval);
          return;
        }

        // success
        if (resWithHandle.data.proposed_plan) {
          stateStatus.value = StepStateEnum.SUCCESS;
          const proposed_plan = resWithHandle.data.proposed_plan;
          emits('storeCurrentStepData', { token, auth_token, proposed_plan });
          clearInterval(pollingInventoringInterval);
          emits('updateStep');
          return;
        }
      } catch (err: any) {
        stateStatus.value = StepStateEnum.ERROR;
        errorMessage.value =
          err.message ||
          'An error occurred while inventoring the account. Try again';
        clearInterval(pollingInventoringInterval);
        return;
      }
    };

    const pollingInventoringInterval = setInterval(
      pollInventoryCustomerAccount,
      POLL_INTERVAL
    );
  } catch (err: any) {
    stateStatus.value = StepStateEnum.ERROR;
    errorMessage.value = err.message;
  }
}
</script>
