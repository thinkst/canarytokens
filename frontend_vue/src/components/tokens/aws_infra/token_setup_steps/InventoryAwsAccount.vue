<template>
  <h2 class="step-title">Inventoring Done!</h2>
  <div v-if="isLoading">Loading...</div>

    <p v-if="!isLoading && !isError">
      We have completed the inventory of your account. <br />We will proceed to
      generate the plan for you in
      <span class="font-semibold">{{ countdownSeconds }}</span> second{{
        countdownSeconds > 1 ? 's' : ''
      }}.
    </p>
  </section>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { requestInventoryCustomerAccount } from '@/api/awsInfra.ts';
import type { TokenDataType } from '@/utils/dataService';
import { useCountdown } from '@/utils/useCountdown';
import StepState from '../StepState.vue';

const emits = defineEmits(['updateStep', 'storeFetchedData']);

const props = defineProps<{
  initialStepData: TokenDataType;
}>();

const isLoading = ref(true);
const isError = ref(false);
const isSuccess = ref(false);
const errorMessage = ref('');

const { token, auth_token } = props.initialStepData;

const { countdownSeconds, triggerCountdown } = useCountdown(5);

onMounted(async () => {
  await handleInventory();
});

async function handleInventory() {
  const POLL_INTERVAL = 5000;

  isLoading.value = true;
  isError.value = false;
  isSuccess.value = false;

  try {
    const res = await requestInventoryCustomerAccount({
      canarytoken: token,
      auth_token,
    });

    if (res.status !== 200) {
      isLoading.value = false;
      isError.value = true;
      errorMessage.value = res.data.error_message;
    }

    const handle = res.data.handle;

    const startTime = Date.now();
    const timeout = 5 * 60 * 1000; // 5 minutes

    const pollInventoryCustomerAccount = async () => {
      try {
        const resWithHandle = await requestInventoryCustomerAccount({ handle });

        if (resWithHandle.status !== 200) {
          isLoading.value = false;
          isError.value = true;
          errorMessage.value = resWithHandle.data.error;
          clearInterval(pollingInventoringInterval);
          return;
        }

        if (resWithHandle.data.error) {
          isLoading.value = false;
          isError.value = true;
          errorMessage.value = resWithHandle.data.error;
          clearInterval(pollingInventoringInterval);
          return;
        }

        // timeout
        if (Date.now() - startTime >= timeout) {
          isLoading.value = false;
          isError.value = true;
          errorMessage.value = 'The operation took too long. Try again.';
          clearInterval(pollingInventoringInterval);
          return;
        }

        // success
        if (resWithHandle.data.proposed_plan) {
          isLoading.value = false;
          isSuccess.value = true;
          const proposed_plan = resWithHandle.data.proposed_plan;
          emits('storeCurrentStepData', { token, auth_token, proposed_plan });
          clearInterval(pollingInventoringInterval);
          await triggerCountdown().then(() => {
            emits('updateStep');
          });
          return;
        }
      } catch (err: any) {
        isError.value = true;
        errorMessage.value =
          err.message ||
          'An error occurred while inventoring the account. Try again';
        clearInterval(pollingInventoringInterval);
        return;
      } finally {
        isLoading.value = false;
        return;
      }
    };

    const pollingInventoringInterval = setInterval(
      pollInventoryCustomerAccount,
      POLL_INTERVAL
    );
  } catch (err: any) {
    isError.value = true;
    errorMessage.value = err.message;
    isSuccess.value = false;
  }
}
</script>
