import * as yup from 'yup';
import { getFieldLabel } from '@/components/tokens/aws_infra/plan_generator/assetService.ts';
import type { AssetData } from '@/components/tokens/aws_infra/types.ts';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';

const requiredString = (assetType: AssetTypesEnum, labelKey: string) =>
  yup
    .string()
    .required()
    .label(getFieldLabel(assetType, labelKey as keyof AssetData));

export const S3Bucket_schema = yup.object().shape({
  bucket_name: requiredString(AssetTypesEnum.S3BUCKET, 'bucket_name'),
  objects: yup
    .array()
    .of(
      yup
        .string()
        .required()
        .label(getFieldLabel(AssetTypesEnum.S3BUCKET, 'objects'))
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
  ssm_parameter_name: requiredString(
    AssetTypesEnum.SSMPARAMETER,
    'ssm_parameter_name'
  ),
});

export const SecretsManagerSecret_schema = yup.object().shape({
  secret_name: requiredString(
    AssetTypesEnum.SECRETMANAGERSECRET,
    'secret_name'
  ),
});

export const DynamoDBTable_schema = yup.object().shape({
  table_name: requiredString(AssetTypesEnum.DYNAMODBTABLE, 'table_name'),
  table_items: yup
    .array()
    .of(
      yup
        .string()
        .required()
        .label(getFieldLabel(AssetTypesEnum.DYNAMODBTABLE, 'table_items'))
    ),
});

export const Default_schema = yup.object();
