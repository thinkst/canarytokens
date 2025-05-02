import { ref } from 'vue';
import { deleteToken } from '@/api/awsInfra';

export function useDeleteToken(auth_token: string, token: string) {
  const isError = ref(false);
  const isErrorMessage = ref('');
  const isLoading = ref(false);
  const isSuccess = ref(false);

  async function deleteTokenFnc() {
    const POLL_INTERVAL = 5000;

    isLoading.value = true;
    isError.value = false;

    try {
      const res = await deleteToken({
        canarytoken: token,
        auth_token,
      });
      if (res.status !== 200) {
        isLoading.value = false;
        isError.value = true;
        isErrorMessage.value = res.data.message;
      }

      const handle = res.data.handle;

      const startTime = Date.now();
      const timeout = 5 * 60 * 1000; // 5 minutes

      const pollDeleteToken = async () => {
        try {
          const resWithHandle = await deleteToken({ handle });

          if (resWithHandle.status !== 200) {
            isLoading.value = false;
            isError.value = true;
            isErrorMessage.value =
              resWithHandle.data.error ||
              'Error on requesting to delete the token';
            clearInterval(pollingDeleteTokenInterval);
            return;
          }

          if (resWithHandle.data.message) {
            isLoading.value = false;
            isError.value = true;
            isErrorMessage.value = resWithHandle.data.message;
            clearInterval(pollingDeleteTokenInterval);
            return;
          }

          // timeout
          if (Date.now() - startTime >= timeout) {
            isError.value = true;
            isErrorMessage.value = 'The operation took too long. Try again.';
            clearInterval(pollingDeleteTokenInterval);
            return;
          }

          // success
          if (resWithHandle.data.terraform_module_snippet) {
            isLoading.value = false;
            isSuccess.value = true;
            clearInterval(pollingDeleteTokenInterval);
            return;
          }
        } catch (err: any) {
          isError.value = true;
          isErrorMessage.value =
            err.message ||
            'An error occurred while deleting the token. Try again';
          clearInterval(pollingDeleteTokenInterval);
          return;
        } finally {
          isLoading.value = false;
        }
      };

      const pollingDeleteTokenInterval = setInterval(
        pollDeleteToken,
        POLL_INTERVAL
      );
    } catch (err: any) {
      isError.value = true;
      isErrorMessage.value = err.message;
      isSuccess.value = false;
    }
  }

  return {
    deleteTokenFnc,
    isErrorMessage,
    isLoading,
    isSuccess,
  };
}
