import * as Yup from 'yup';
import { TOKENS_TYPE } from '@/components/constants.ts';
import { ref } from 'vue';
import type { Ref } from 'vue';

type FieldsType = {
  email: string;
  memo: string;
};

type ValidateSchemaType = {
  [key: string]: {
    schema: Yup.ObjectSchema<FieldsType>;
  };
};

export function useValidation() {
  const validationSchema: Ref<ValidateSchemaType> = ref({
    [TOKENS_TYPE.WEBBUG]: {
      schema: Yup.object().shape({
        email: Yup.string().email().required(),
        memo: Yup.string().required(),
      }),
    },
    [TOKENS_TYPE.DNS]: {
      schema: Yup.object().shape({
        email: Yup.string().email().required(),
        memo: Yup.string().required(),
      }),
    },
    [TOKENS_TYPE.QRCODE]: {
      schema: Yup.object().shape({
        email: Yup.string().email().required(),
        memo: Yup.string().required(),
      }),
    },
    [TOKENS_TYPE.MYSQL]: {
      schema: Yup.object().shape({
        email: Yup.string().email().required(),
        memo: Yup.string().required(),
      }),
    },
  });

  return {
    validationSchema,
  };
}
