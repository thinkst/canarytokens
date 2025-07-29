import { ref, watch } from 'vue';
import type { Ref } from 'vue';
import {
  requestAWSInfraRoleCheck,
  requestInventoryCustomerAccount,
} from '@/api/awsInfra.ts';
import { StepStateEnum } from '@/components/tokens/aws_infra/useStepState.ts';

export function useFetchUserAccount(
  canarytoken: string,
  auth_token: string,
  external_id?: Ref<string>
) {
  const errorMessage = ref('');
  const stateStatus = ref<StepStateEnum>();
  const proposedPlan = ref<any>(null);
  const externalId = ref(external_id || '');

  const POLL_INTERVAL = 2000;
  // If the first attempts fails, it could depend on the AWS account still being set up
  // so we retry a few times before giving up
  const MAX_RETRIES = 5;

  async function handleFetchUserAccount() {
    await handleCheckRole();
  }

  async function handleCheckRole() {
    errorMessage.value = '';
    stateStatus.value = StepStateEnum.LOADING;
    let retryAttempts = 0;

    try {
      const res = await requestAWSInfraRoleCheck({
        canarytoken,
        auth_token,
        external_id: externalId.value || '',
      });
      if (res.status !== 200) {
        stateStatus.value = StepStateEnum.ERROR;
        errorMessage.value = res.data.message;
        return;
      }

      const handle = res.data.handle;

      const pollInfraRoleCheck = async () => {
        try {
          const resWithHandle = await requestAWSInfraRoleCheck({
            handle,
          });

          // success
          if (
            resWithHandle.status === 200 &&
            resWithHandle.data.session_credentials_retrieved
          ) {
            await handleInventory();
            return;
          }

          if (retryAttempts >= MAX_RETRIES) {
            stateStatus.value = StepStateEnum.ERROR;
            errorMessage.value =
              resWithHandle.data?.error ||
              resWithHandle.data?.message ||
              'Max retries reached';
            return;
          }

          setTimeout(() => {
            console.log(
              `Retrying AWS Infra Role Check (${retryAttempts}/${MAX_RETRIES})`
            );
            retryAttempts++;
            pollInfraRoleCheck();
          }, POLL_INTERVAL);
        } catch (err: any) {
          if (retryAttempts >= MAX_RETRIES) {
            stateStatus.value = StepStateEnum.ERROR;
            errorMessage.value =
              err.response?.data?.message ||
              'An error occurred while checking the Role. Try again';
            return;
          }
          console.log(
            `Retrying AWS Infra Role Check (${retryAttempts}/${MAX_RETRIES})`
          );

          setTimeout(() => {
            retryAttempts++;
            pollInfraRoleCheck();
          }, POLL_INTERVAL);
        }
      };

      await pollInfraRoleCheck();
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
        return;
      }

      const handle = res.data.handle;
      let retryAttempts = 0;

      const pollInventoryCustomerAccount = async () => {
        try {
          const resWithHandle = await requestInventoryCustomerAccount({
            handle,
          });

          // success
          if (resWithHandle.data.proposed_plan) {
            stateStatus.value = StepStateEnum.SUCCESS;
            proposedPlan.value = resWithHandle.data.proposed_plan;
            return;
          }

          // retry
          if (retryAttempts >= MAX_RETRIES) {
            stateStatus.value = StepStateEnum.ERROR;
            errorMessage.value = 'Max retries reached';
            return;
          }

          // Retry after delay
          setTimeout(() => {
            console.log(
              `Retrying Inventory Customer Account (${retryAttempts}/${MAX_RETRIES})`
            );
            retryAttempts++;
            pollInventoryCustomerAccount();
          }, POLL_INTERVAL);
        } catch (err: any) {
          if (retryAttempts >= MAX_RETRIES) {
            stateStatus.value = StepStateEnum.ERROR;
            errorMessage.value =
              'An error occurred while inventoring the account. Try again';
            return;
          }

          setTimeout(() => {
            console.log(
              `Retrying Inventory Customer Account (${retryAttempts}/${MAX_RETRIES})`
            );
            retryAttempts++;
            pollInventoryCustomerAccount();
          }, POLL_INTERVAL);
        }
      };

      await pollInventoryCustomerAccount();
    } catch (err: any) {
      stateStatus.value = StepStateEnum.ERROR;
      errorMessage.value = err.message;
    }
  }

  watch(
    () => external_id,
    (newValue) => {
      externalId.value = newValue || '';
    }
  );

  return {
    errorMessage,
    stateStatus,
    handleFetchUserAccount,
    proposedPlan,
  };
}
