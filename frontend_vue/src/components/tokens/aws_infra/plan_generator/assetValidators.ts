import * as yup from 'yup';
import { ASSET_LABEL } from '../constants.ts';

const requiredString = (labelKey: keyof typeof ASSET_LABEL) =>
  yup.string().required().label(ASSET_LABEL[labelKey]);

export const S3Bucket_schema = yup.object().shape({
  bucket_name: requiredString('bucket_name'),
  objects: yup.array().of(
    yup.object().shape({
      object_path: yup.string().required().label(ASSET_LABEL['object_path']),
    })
  ),
});

export const SQSQueue_schema = yup.object().shape({
  queue_name: requiredString('queue_name'),
  message_count: yup
    .number()
    .typeError(`${ASSET_LABEL['message_count']} must be a number`)
    .required(ASSET_LABEL['message_count']),
});

export const SSMParameter_schema = yup.object().shape({
  ssm_parameter_value: requiredString('ssm_parameter_value'),
  ssm_parameter_name: requiredString('ssm_parameter_name'),
});

export const SecretsManagerSecret_schema = yup.object().shape({
  ssm_parameter_value: requiredString('ssm_parameter_value'),
  ssm_parameter_name: requiredString('ssm_parameter_name'),
});

export const DynamoDBTable_schema = yup.object().shape({
  dynamodb_partition_key: requiredString('dynamodb_partition_key'),
  dynamodb_name: requiredString('dynamodb_name'),
  dynamodb_row_count: yup
    .number()
    .typeError(`${ASSET_LABEL['dynamodb_row_count']} must be a number`)
    .required(ASSET_LABEL['dynamodb_row_count']),
});

export const Default_schema = yup.object();
