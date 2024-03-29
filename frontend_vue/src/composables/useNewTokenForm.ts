import { ref, watch } from 'vue';
import type { Ref } from 'vue';
import { store } from '@/store/store.ts';

export function useNewTokenForm<T>(initialValue: any): {
  formData: Ref<T>;
} {
  const formData = ref(initialValue);

  watch(
    formData,
    (newVal) => {
      if (!newVal) return;
      store.newTokenData = formData.value;
    },
    { deep: true }
  );

  return { formData };
}
