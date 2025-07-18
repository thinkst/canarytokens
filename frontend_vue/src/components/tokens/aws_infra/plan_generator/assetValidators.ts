import * as yup from 'yup';
import { getFieldLabel } from '@/components/tokens/aws_infra/assetService.ts';
import type { AssetData } from '@/components/tokens/aws_infra/types.ts';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';

const requiredString = (assetType: AssetTypesEnum, labelKey: string) =>
  yup
    .string()
    .required()
    .label(getFieldLabel(assetType, labelKey as keyof AssetData));

export const S3Bucket_schema = yup.object().shape({
  bucket_name: requiredString(AssetTypesEnum.S3BUCKET, 'bucket_name'),
  objects: yup.array().of(
    yup.object().shape({
      object_path: yup
        .string()
        .required()
        .label(getFieldLabel(AssetTypesEnum.S3BUCKET, 'object_path')),
    })
  ),
});

export const SQSQueue_schema = yup.object().shape({
  queue_name: requiredString(AssetTypesEnum.SQSQUEUE, 'queue_name'),
  message_count: yup
    .number()
    .typeError(
      `${getFieldLabel(AssetTypesEnum.SQSQUEUE, 'message_count')} must be a number`
    )
    .required(getFieldLabel(AssetTypesEnum.SQSQUEUE, 'message_count')),
});

export const SSMParameter_schema = yup.object().shape({
  ssm_parameter_value: requiredString(
    AssetTypesEnum.SSMPARAMETER,
    'ssm_parameter_value'
  ),
  ssm_parameter_name: requiredString(
    AssetTypesEnum.SSMPARAMETER,
    'ssm_parameter_name'
  ),
});

export const SecretsManagerSecret_schema = yup.object().shape({
  secretsmanager_secret_name: requiredString(
    AssetTypesEnum.SECRETMANAGERSECRET,
    'secretsmanager_secret_name'
  ),
  secretsmanager_secret_value: requiredString(
    AssetTypesEnum.SECRETMANAGERSECRET,
    'secretsmanager_secret_value'
  ),
});

export const DynamoDBTable_schema = yup.object().shape({
  dynamodb_partition_key: requiredString(
    AssetTypesEnum.DYNAMODBTABLE,
    'dynamodb_partition_key'
  ),
  dynamodb_name: requiredString(AssetTypesEnum.DYNAMODBTABLE, 'dynamodb_name'),
  dynamodb_row_count: yup
    .number()
    .typeError(
      `${getFieldLabel(AssetTypesEnum.DYNAMODBTABLE, 'dynamodb_row_count')} must be a number`
    )
    .required(
      getFieldLabel(AssetTypesEnum.DYNAMODBTABLE, 'dynamodb_row_count')
    ),
});

export const Default_schema = yup.object();
