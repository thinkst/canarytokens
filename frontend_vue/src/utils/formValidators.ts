import * as Yup from 'yup';
import { TOKENS_TYPE } from '@/components/constants.ts';

type FieldsType = {
  email: string;
  memo: string;
};

type ValidateSchemaType = {
  [key: string]: {
    schema: Yup.ObjectSchema<FieldsType>;
  };
};

export const formValidators: ValidateSchemaType = {
  [TOKENS_TYPE.WEB_BUG]: {
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
};
