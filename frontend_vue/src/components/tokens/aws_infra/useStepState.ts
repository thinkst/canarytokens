import type { Ref } from 'vue';
import { watch, ref } from 'vue';

export enum StepStateEnum {
  LOADING = 'loading',
  ERROR = 'error',
  SUCCESS = 'success',
}

export function useStepState(state: Ref<StepStateEnum>) {
  const isLoading = ref(false);
  const isError = ref(false);
  const isSuccess = ref(false);

  watch(
    state,
    (newValue) => {
      isLoading.value = newValue === StepStateEnum.LOADING;
      isError.value = newValue === StepStateEnum.ERROR;
      isSuccess.value = newValue === StepStateEnum.SUCCESS;
    },
    { immediate: true }
  );

  return {
    isLoading,
    isError,
    isSuccess,
  };
}
