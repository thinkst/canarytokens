import { AssetTypesEnum } from './constants';

type S3ObjectData = {
  object_path: string;
};

type S3BucketData = {
  bucket_name: string;
  objects: S3ObjectData[] | [];
  off_inventory?: boolean;
};

type SQSQueueData = {
  queue_name: string;
  message_count: number | null;
  off_inventory?: boolean;
};

type SSMParameterData = {
  ssm_parameter_name: string;
  ssm_parameter_value: string;
  off_inventory?: boolean;
};

type SecretsManagerSecretData = {
  secretsmanager_secret_name: string;
  secretsmanager_secret_value: string;
  off_inventory?: boolean;
};

type DynamoDBTableData = {
  dynamodb_name: string;
  dynamodb_partition_key: string;
  dynamodb_row_count: number | null;
  off_inventory?: boolean;
};

type ProposedAWSInfraTokenPlanData = {
  [K in AssetTypesEnum]?: AssetData[] | null;
};

type AssetData =
  | DynamoDBTableData
  | SecretsManagerSecretData
  | SSMParameterData
  | SQSQueueData
  | S3BucketData;

type TokenSetupData = {
  token: string;
  auth_token: string;
  proposed_plan: {
    assets: ProposedAWSInfraTokenPlanData;
  };
  code_snippet_command?: string;
};

export type {
  AssetData,
  S3BucketData,
  S3ObjectData,
  SQSQueueData,
  SSMParameterData,
  SecretsManagerSecretData,
  DynamoDBTableData,
  TokenSetupData,
  ProposedAWSInfraTokenPlanData,
};
