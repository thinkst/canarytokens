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
        isErrorMessage.value =
          res.data.message ||
          'Error on requesting to delete the token. Try again';
        return;
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
              'Error on requesting to delete the token. Try again';
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
            isLoading.value = false;
            isError.value = true;
            isErrorMessage.value = 'The operation took too long. Try again.';
            clearInterval(pollingDeleteTokenInterval);
            return;
          }

          // success
          if (resWithHandle.data.result === true) {
            isLoading.value = false;
            isSuccess.value = true;
            clearInterval(pollingDeleteTokenInterval);
            return;
          }
        } catch (err: any) {
          isError.value = true;
          isErrorMessage.value =
            'Error on requesting to delete the token. Try again';
          clearInterval(pollingDeleteTokenInterval);
          return;
        }
      };

      const pollingDeleteTokenInterval = setInterval(
        pollDeleteToken,
        POLL_INTERVAL
      );
    } catch (err: any) {
      isLoading.value = false;
      isError.value = true;
      isErrorMessage.value =
        'Error on requesting to delete the token. Try again';
      isSuccess.value = false;
      clearInterval(pollingDeleteTokenInterval);
    }
  }

  return {
    deleteTokenFnc,
    isErrorMessage,
    isLoading,
    isSuccess,
  };
}
