import { ref } from 'vue';
import {
  requestAWSInfraRoleCheck,
  requestInventoryCustomerAccount,
} from '@/api/awsInfra.ts';
import { StepStateEnum } from '@/components/tokens/aws_infra/useStepState.ts';

export function useFetchUserAccount(canarytoken: string, auth_token: string) {
  const errorMessage = ref('');
  const stateStatus = ref<StepStateEnum>();
  const proposedPlan = ref<any>(null);

  const POLL_INTERVAL = 2000;

  async function handleFetchUserAccount() {
    await handleCheckRole();
  }

  async function handleCheckRole() {
    errorMessage.value = '';
    stateStatus.value = StepStateEnum.LOADING;

    try {
      const res = await requestAWSInfraRoleCheck({
        canarytoken,
        auth_token,
      });
      if (res.status !== 200) {
        stateStatus.value = StepStateEnum.ERROR;
        errorMessage.value = res.data.message;
        // emits('isSettingError', true);
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
            // emits('isSettingError', true);
            clearInterval(pollingRoleInterval);
            return;
          }

          if (resWithHandle.data.error) {
            stateStatus.value = StepStateEnum.ERROR;
            errorMessage.value = resWithHandle.data.error;
            // emits('isSettingError', true);
            clearInterval(pollingRoleInterval);
            return;
          }

          // timeout
          if (Date.now() - startTime >= timeout) {
            stateStatus.value = StepStateEnum.ERROR;
            errorMessage.value = 'The operation took too long. Try again.';
            // emits('isSettingError', true);
            clearInterval(pollingRoleInterval);
            return;
          }

          // success
          if (resWithHandle.data.session_credentials_retrieved) {
            clearInterval(pollingRoleInterval);
            await handleInventory();
            return;
          }
        } catch (err: any) {
          stateStatus.value = StepStateEnum.ERROR;
          errorMessage.value =
            err.message ||
            'An error occurred while checking the Role. Try again';
          clearInterval(pollingRoleInterval);
          return;
        }
      };

      const pollingRoleInterval = setInterval(
        pollInfraRoleCheck,
        POLL_INTERVAL
      );
    } catch (err: any) {
      stateStatus.value = StepStateEnum.ERROR;
      errorMessage.value = err.message;
    }
  }

  async function handleInventory() {
    errorMessage.value = '';
    stateStatus.value = StepStateEnum.LOADING;

    try {
      const res = await requestInventoryCustomerAccount({
        canarytoken,
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
          const resWithHandle = await requestInventoryCustomerAccount({
            handle,
          });

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
            proposedPlan.value = resWithHandle.data.proposed_plan;
            clearInterval(pollingInventoringInterval);
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

  return {
    errorMessage,
    stateStatus,
    handleFetchUserAccount,
    proposedPlan,
  };
}
