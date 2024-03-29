import { reactive } from 'vue';

type T = { [key: string]: string } | object;

export const store = reactive<{ newTokenData: T }>({
  newTokenData: {} as T,
});
