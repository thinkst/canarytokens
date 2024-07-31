import * as Yup from 'yup';
import { TOKENS_TYPE, MAX_UPLOAD_SIZE } from '@/components/constants.ts';
import { isValidFileType, validFileExtensions } from './utils';

type FieldsType = {
  email: string | undefined;
  memo: string;
  webhook_url: string | undefined;
};

type ValidateSchemaType = {
  [key: string]: {
    schema: Yup.ObjectSchema<FieldsType>;
  };
};

const validationMessages = {
  validEmail: 'It must be a valid email',
  validURL: 'It must be a valid URL',
  provideMemo: 'Memo is a required field',
  maxLengthMemo: 'Memo cannot be longer than 1000 characters',
  provideEmail: 'Provide a valid email',
};

const validationNotificationSettings = {
  email: Yup.string()
    .email(validationMessages.validEmail)
    .required(validationMessages.provideEmail),
  memo: Yup.string()
    .required(validationMessages.provideMemo)
    .max(1000, validationMessages.maxLengthMemo)
    .test('empty-check', validationMessages.provideMemo, val => val.trim().length !== 0),
  webhook_url: Yup.string()
        .url(validationMessages.validURL),
};

export const formValidators: ValidateSchemaType = {
  [TOKENS_TYPE.WEB_BUG]: {
    schema: Yup.object().shape(validationNotificationSettings),
  },
  [TOKENS_TYPE.DNS]: {
    schema: Yup.object().shape(validationNotificationSettings),
  },
  [TOKENS_TYPE.QRCODE]: {
    schema: Yup.object().shape(validationNotificationSettings),
  },
  [TOKENS_TYPE.MYSQL]: {
    schema: Yup.object().shape(validationNotificationSettings),
  },
  [TOKENS_TYPE.LOG4SHELL]: {
    schema: Yup.object().shape(validationNotificationSettings),
  },
  [TOKENS_TYPE.AWS_KEYS]: {
    schema: Yup.object().shape(validationNotificationSettings),
  },
  [TOKENS_TYPE.FAST_REDIRECT]: {
    schema: Yup.object().shape({
      ...validationNotificationSettings,
      redirect_url: Yup.string().required('A redirect URL is required'),
    }),
  },
  [TOKENS_TYPE.SLOW_REDIRECT]: {
    schema: Yup.object().shape({
      ...validationNotificationSettings,
      redirect_url: Yup.string().required('A redirect URL is required'),
    }),
  },
  [TOKENS_TYPE.SENSITIVE_CMD]: {
    schema: Yup.object().shape({
      ...validationNotificationSettings,
      cmd_process: Yup.string()
        .required('A process name is required')
        .test('containsExe', 'File name must end in .exe', (value) => {
          return value && value.endsWith('.exe') ? true : false;
        }),
    }),
  },
  [TOKENS_TYPE.MICROSOFT_EXCEL]: {
    schema: Yup.object().shape(validationNotificationSettings),
  },
  [TOKENS_TYPE.AZURE_ID]: {
    schema: Yup.object().shape({
      ...validationNotificationSettings,
      azure_id_cert_file_name: Yup.string()
        .required('Azure ID certificate name is required')
        .test('containsPem', 'File name must end in .pem', (value) => {
          return value && value.endsWith('.pem') ? true : false;
        }),
    }),
  },
  [TOKENS_TYPE.MICROSOFT_WORD]: {
    schema: Yup.object().shape(validationNotificationSettings),
  },
  [TOKENS_TYPE.WEB_IMAGE]: {
    schema: Yup.object().shape({
      ...validationNotificationSettings,
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
        )
        .test(
          'fileTooLarge',
          'Image size must be below 1MB',
          (value) => value.size < MAX_UPLOAD_SIZE
        ),
    }),
  },
  [TOKENS_TYPE.SVN]: {
    schema: Yup.object().shape(validationNotificationSettings),
  },
  [TOKENS_TYPE.UNIQUE_EMAIL]: {
    schema: Yup.object().shape(validationNotificationSettings),
  },
  [TOKENS_TYPE.PDF]: {
    schema: Yup.object().shape(validationNotificationSettings),
  },
  [TOKENS_TYPE.WINDOWS_FOLDER]: {
    schema: Yup.object().shape(validationNotificationSettings),
  },
  [TOKENS_TYPE.CUSTOM_EXE]: {
    schema: Yup.object().shape({
      ...validationNotificationSettings,
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
        )
        .test(
          'fileTooLarge',
          'File size must be below 1MB',
          (value) => value.size < MAX_UPLOAD_SIZE
        ),
    }),
  },
  [TOKENS_TYPE.SQL_SERVER]: {
    schema: Yup.object().shape({
      ...validationNotificationSettings,
      sql_server_sql_action: Yup.string().required('SQL Action is required'),
      sql_server_table_name: Yup.string().when('sql_server_sql_action', {
        is: (sql_server_sql_action: string) =>
          sql_server_sql_action !== 'SELECT',
        then: () => Yup.string().required('Table Name is required'),
      }),
      sql_server_view_name: Yup.string().when('sql_server_sql_action', {
        is: (sql_server_sql_action: string) =>
          sql_server_sql_action === 'SELECT',
        then: () => Yup.string().required('Name SQL Server view is required'),
      }),
    }),
  },
  [TOKENS_TYPE.CLONED_WEBSITE]: {
    schema: Yup.object().shape({
      ...validationNotificationSettings,
      clonedsite: Yup.string().required('Domain is required'),
    }),
  },
  [TOKENS_TYPE.CSS_CLONED_SITE]: {
    schema: Yup.object().shape({
      ...validationNotificationSettings,
      expected_referrer: Yup.string().required('Domain is required'),
    }),
  },
  [TOKENS_TYPE.KUBECONFIG]: {
    schema: Yup.object().shape(validationNotificationSettings),
  },
  [TOKENS_TYPE.WIREGUARD]: {
    schema: Yup.object().shape(validationNotificationSettings),
  },
  [TOKENS_TYPE.AZURE_ENTRA_CONFIG]: {
    schema: Yup.object().shape(validationNotificationSettings),
  },
  [TOKENS_TYPE.PWA]: {
    schema: Yup.object().shape({
      ...validationNotificationSettings,
      app_name: Yup.string(),//.required('An app name is required'),
      icon: Yup.string(),//.required('An icon is required'),
    }),
  },
};
