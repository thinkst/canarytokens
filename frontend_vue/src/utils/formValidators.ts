import * as Yup from 'yup';
import { TOKENS_TYPE } from '@/components/constants.ts';
import { isValidFileType, validFileExtensions } from './utils';

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
  [TOKENS_TYPE.SENSITIVE_CMD]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        cmd_process: Yup.string()
          .required('A process name is required')
          .test('containsExe', 'File name must end in .exe', (value) => {
            return value && value.endsWith('.exe') ? true : false;
          }),
        memo: Yup.string().required(validationMessages.provideMemo),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.MICROSOFT_EXCEL]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        memo: Yup.string().required(validationMessages.provideMemo),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.AZURE_ID]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        azure_id_cert_file_name: Yup.string()
          .required('Azure ID certificate name is required')
          .test('containsPem', 'File name must end in .pem', (value) => {
            return value && value.endsWith('.pem') ? true : false;
          }),
        memo: Yup.string().required(validationMessages.provideMemo),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.MICROSOFT_WORD]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        memo: Yup.string().required(validationMessages.provideMemo),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.WEB_IMAGE]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        memo: Yup.string().required(validationMessages.provideMemo),
        web_image: Yup.mixed<File>()
          .required('Image is Required')
          .test(
            'validType',
            'Not a valid image type',
            (value) =>
              isValidFileType(
                value && value.name.toLowerCase(),
                validFileExtensions.image
              ) as boolean
          ),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.SVN]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        memo: Yup.string().required(validationMessages.provideMemo),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.UNIQUE_EMAIL]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        memo: Yup.string().required(validationMessages.provideMemo),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.PDF]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        memo: Yup.string().required(validationMessages.provideMemo),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.CUSTOM_EXE]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        memo: Yup.string().required(validationMessages.provideMemo),
        signed_exe: Yup.mixed<File>()
          .required('File is Required')
          .test(
            'validType',
            'Not a valid file type: expected EXE or DLL',
            (value) =>
              isValidFileType(
                value && value.name.toLowerCase(),
                validFileExtensions.exe
              ) as boolean
          ),
      },
      [['webhook_url', 'email']]
    ),
  },
  [TOKENS_TYPE.SQL_SERVER]: {
    schema: Yup.object().shape(
      {
        ...validationSchemaEmailOrUrl,
        memo: Yup.string().required(validationMessages.provideMemo),
        sql_server_sql_action: Yup.string().required('SQL Action is required'),
        sql_server_table_name: Yup.string().when('sql_server_sql_action', {
          is: (sql_server_sql_action: string) =>
            sql_server_sql_action !== 'SELECT',
          then: () => Yup.string().required('Table Name is required'),
        }),
        sql_server_trigger_name: Yup.string().when('sql_server_sql_action', {
          is: (sql_server_sql_action: string) =>
            sql_server_sql_action !== 'SELECT',
          then: () => Yup.string().required('Trigger Name is required'),
        }),
        sql_server_view_name: Yup.string().when('sql_server_sql_action', {
          is: (sql_server_sql_action: string) =>
            sql_server_sql_action === 'SELECT',
          then: () => Yup.string().required('Name SQL Server view is required'),
        }),
        sql_server_function_name: Yup.string().when('sql_server_sql_action', {
          is: (sql_server_sql_action: string) =>
            sql_server_sql_action === 'SELECT',
          then: () =>
            Yup.string().required('Name SQL Server function is required'),
        }),
      },
      [['webhook_url', 'email']]
    ),
  },
};
