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
  sqs_queue_name: requiredString('sqs_queue_name')
});

export const SSMParameter_schema = yup.object().shape({
  ssm_parameter_name: requiredString('ssm_parameter_name'),
});

export const SecretsManagerSecret_schema = yup.object().shape({
  secret_name: requiredString('secret_name'),
});

export const DynamoDBTable_schema = yup.object().shape({
  table_name: requiredString('table_name'),
  table_items: yup.array().of(
    yup.string().required().label(ASSET_LABEL['table_items'])
  ),
});

export const Default_schema = yup.object();
