import * as yup from 'yup';
import { getFieldLabel } from '@/components/tokens/aws_infra/plan_generator/assetService.ts';
import type { AssetData } from '@/components/tokens/aws_infra/types.ts';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';

const regexIsIPV4 = /^\d{1,3}(\.\d{1,3}){3}$/;
const regexS3BucketNameChars = /^[a-z0-9][a-z0-9.\-]*[a-z0-9]$/;

const regexS3BucketNameForbiddenPrefixes =
  /^(?!(xn--|sthree-|sthree-configurator|s3alias|s3-|s3control-))/;

const regexS3Objects = /^[a-zA-Z0-9!_.\-~*'()/]+$/;
const regexSQSQueueName = /^[A-Za-z0-9_\-;]+$/;
const regexSSMParameterForbiddenPrefixes = /^(?!aws|ssm)/i;
const regexSSMParameterChars = /^[a-zA-Z0-9_.-]+$/;
const regexSecretsManagerSecretName = /^[A-Za-z0-9/_+=.@-]+$/;
const regexDynamoDBasset = /^[a-zA-Z0-9_.-]+$/;

const requiredString = (assetType: AssetTypesEnum, labelKey: string) =>
  yup
    .string()
    .required()
    .label(getFieldLabel(assetType, labelKey as keyof AssetData));

export const S3Bucket_schema = yup.object().shape({
  bucket_name: requiredString(AssetTypesEnum.S3BUCKET, 'bucket_name')
    .min(3, 'S3 Bucket name must be min 3 characters')
    .max(63, 'S3 Bucket name must be max 63 characters')
    .matches(
      regexS3BucketNameForbiddenPrefixes,
      'S3 Bucket can`t start with xn--, sthree-, sthree-configurator, s3alias, s3-, or s3control-'
    )
    .matches(
      regexS3BucketNameChars,
      'S3 Bucket name must contain only lowercase letters, numbers, dots, or hyphens'
    )
    .test(
      'not-an-ipv4',
      'S3 Bucket name cannot be formatted as an IP address.',
      (val) => (val ? !regexIsIPV4.test(val) : true)
    )
    .test(
      'not-end-with-ol-s3',
      'S3 Bucket name must not end with --ol-s3',
      (val) => (val ? !val.endsWith('--ol-s3') : true)
    ),
  objects: yup
    .array()
    .of(
      yup
        .string()
        .required()
        .max(200, 'S3 Object must be max 200 characters')
        .matches(
          regexS3Objects,
          "S3 Object must contain only alphanumeric characters, !_.-~*'()/"
        )
        .label(getFieldLabel(AssetTypesEnum.S3BUCKET, 'objects'))
    ),
});

export const SQSQueue_schema = yup.object().shape({
  sqs_queue_name: requiredString(AssetTypesEnum.SQSQUEUE, 'sqs_queue_name')
    .max(80, 'SQS Queue name must be max 80 characters')
    .matches(
      regexSQSQueueName,
      'SQS Queue name must contain only letters, numbers, underscores, hyphens, or semicolons'
    ),
});

export const SSMParameter_schema = yup.object().shape({
  ssm_parameter_name: requiredString(
    AssetTypesEnum.SSMPARAMETER,
    'ssm_parameter_name'
  )
    .max(2048, 'SSM Parameter name must be max 2048 characters')
    .matches(
      regexSSMParameterForbiddenPrefixes,
      "SSM Parameter name can't be equal or start with 'aws' and 'ssm'"
    )
    .matches(
      regexSSMParameterChars,
      "SSM Parameter name must contain only letters, numbers, and '._-'."
    ),
});

export const SecretsManagerSecret_schema = yup.object().shape({
  secret_name: requiredString(AssetTypesEnum.SECRETMANAGERSECRET, 'secret_name')
    .max(512, 'Secret name must be max 512 characters')
    .matches(
      regexSecretsManagerSecretName,
      'Secret name must contain only alphanumeric characters, /, _, +, =, ., @, or -'
    ),
});

export const DynamoDBTable_schema = yup.object().shape({
  table_name: requiredString(AssetTypesEnum.DYNAMODBTABLE, 'table_name')
    .max(255, 'Table name must be max 255 characters')
    .matches(
      regexDynamoDBasset,
      'Table name must contain only letters, numbers, underscores, hyphens, or semicolons'
    ),
  table_items: yup
    .array()
    .of(
      yup
        .string()
        .required()
        .max(255, 'Table item must be max 200 characters')
        .matches(
          regexDynamoDBasset,
          'Table item must contain only letters, numbers, underscores, hyphens, or semicolons'
        )
        .label(getFieldLabel(AssetTypesEnum.DYNAMODBTABLE, 'table_items'))
    ),
});

export const Default_schema = yup.object();
