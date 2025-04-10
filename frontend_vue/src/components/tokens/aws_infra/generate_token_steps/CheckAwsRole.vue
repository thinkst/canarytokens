<template>
  <h2 class="step-title">Role checked!</h2>
  <div v-if="isLoading">Loading...</div>

  <p>On the next step you'll be inventoring your account</p>
  <font-awesome-icon
    icon="circle-check"
    aria-hidden="true"
    class="text-green w-[6rem] h-[6rem] mt-24"
  />
  <BaseButton
    v-if="!isLoading"
    class="mt-40"
    @click="emits('updateStep')"
  >
    Continue to inventory</BaseButton
  >
</template>

<script lang="ts" setup>
import { ref } from 'vue';

const emits = defineEmits([
  'updateStep',
  'storeCurrentStepData',
  'isSettingError',
]);

const props = defineProps<{
  stepData: any;
}>();

const isLoading = ref(true);
const isError = ref(false);
const isSuccess = ref(false);
const errorMessage = ref('');

const { token, auth_token } = props.stepData;

onMounted(async () => {
  emits('isSettingError', false);
  await handleCheckRole();
});

async function handleCheckRole() {
  const POLL_INTERVAL = 5000;

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
      errorMessage.value = res.data.message;
      emits('isSettingError', true);
    }

    const handle = res.data.handle;

    const startTime = Date.now();
    const timeout = 5 * 60 * 1000; // 5 minutes

    const pollInfraRoleCheck = async () => {
      try {
        const resWithHandle = await requestAWSInfraRoleCheck({ handle });

        if (resWithHandle.status !== 200) {
          isLoading.value = false;
          isError.value = true;
          errorMessage.value = resWithHandle.data.error;
          emits('isSettingError', true);
          clearInterval(pollingRoleInterval);
          return;
        }

        if (resWithHandle.data.error) {
          isLoading.value = false;
          isError.value = true;
          errorMessage.value = resWithHandle.data.error;
          emits('isSettingError', true);
          clearInterval(pollingRoleInterval);
          return;
        }

        // timeout
        if (Date.now() - startTime >= timeout) {
          isError.value = true;
          errorMessage.value = 'The operation took too long. Try again.';
          emits('isSettingError', true);
          clearInterval(pollingRoleInterval);
          return;
        }

        // success
        if (resWithHandle.data.session_credentials_retrieved) {
          isLoading.value = false;
          isSuccess.value = true;
          emits('storeCurrentStepData', { token, auth_token });
          clearInterval(pollingRoleInterval);
          return;
        }
      } catch (err: any) {
        isError.value = true;
        errorMessage.value =
          err.message || 'An error occurred while checking the Role. Try again';
        emits('isSettingError', true);
        clearInterval(pollingRoleInterval);
        return;
      } finally {
        isLoading.value = false;
      }
    };

    const pollingRoleInterval = setInterval(pollInfraRoleCheck, POLL_INTERVAL);
  } catch (err: any) {
    isError.value = true;
    errorMessage.value = err.message;
    isSuccess.value = false;
    emits('isSettingError', true);
  }
}
</script>
