import * as Yup from 'yup';
import { TOKENS_TYPE } from '@/components/constants.ts';

type FieldsType = {
  email: string | undefined;
  webhook_url: string | undefined;
  memo: string;
};

type ValidateSchemaType = {
  [key: string]: {
    schema: Yup.ObjectSchema<FieldsType>;
  };
};

const validationMessages = {
  provideEmailOrUrl: 'Provide at least a valid email or a webhook URL',
  provideMemo: 'Memo is a required field',
};

const validationSchemaEmailOrUrl = {
  email: Yup.string()
    .email()
    .when('webhook_url', {
      is: (webhook_url: string) => !webhook_url || webhook_url.length === 0,
      then: () =>
        Yup.string().email().required(validationMessages.provideEmailOrUrl),
    }),
  webhook_url: Yup.string()
    .url()
    .when('email', {
      is: (email: string) => !email || email.length === 0,
      then: () => Yup.string().required(validationMessages.provideEmailOrUrl),
    }),
};

export const formValidators: ValidateSchemaType = {
  [TOKENS_TYPE.WEB_BUG]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        memo: Yup.string().required(validationMessages.provideMemo),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.DNS]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        memo: Yup.string().required(validationMessages.provideMemo),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.QRCODE]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        memo: Yup.string().required(validationMessages.provideMemo),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.MYSQL]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        memo: Yup.string().required(validationMessages.provideMemo),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.LOG4SHELL]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        memo: Yup.string().required(validationMessages.provideMemo),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.AWS_KEYS]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        memo: Yup.string().required(validationMessages.provideMemo),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.FAST_REDIRECT]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        redirect_url: Yup.string().required('A redirect URL is required'),
        memo: Yup.string().required(validationMessages.provideMemo),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.SLOW_REDIRECT]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        redirect_url: Yup.string().required('A redirect URL is required'),
        memo: Yup.string().required(validationMessages.provideMemo),
      },
      [['webhook_url', 'email']]
    ),
  },
};
