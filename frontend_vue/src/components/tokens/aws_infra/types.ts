import { AssetTypesEnum } from './constants';

type S3ObjectType = {
  object_path: string;
};

type S3BucketType = {
  bucket_name: string;
  objects: S3ObjectType[] | [];
  off_inventory?: boolean;
};

type SQSQueueType = {
  queue_name: string;
  message_count: number | null;
  off_inventory?: boolean;
};

type SSMParameterType = {
  ssm_parameter_name: string;
  ssm_parameter_value: string;
  off_inventory?: boolean;
};

type SecretsManagerSecretType = {
  secretsmanager_secret_name: string;
  secretsmanager_secret_value: string;
  off_inventory?: boolean;
};

type DynamoDBTableType = {
  dynamodb_name: string;
  dynamodb_partition_key: string;
  dynamodb_row_count: number | null;
  off_inventory?: boolean;
};

type AssetTypes = {
  [K in AssetTypesEnum]?: AssetType[] | null;
};

type AssetType =
  | DynamoDBTableType
  | SecretsManagerSecretType
  | SSMParameterType
  | SQSQueueType
  | S3BucketType

type AssetPropertyKey = keyof AssetType;

type FirstStepTokenDataType = {
  token: string;
  auth_token: string;
  proposed_plan: {
    assets: AssetTypes;
  };
  code_snippet_command?: string;
};


export type {
  AssetType,
  AssetTypes,
  S3BucketType,
  S3ObjectType,
  SQSQueueType,
  SSMParameterType,
  SecretsManagerSecretType,
  DynamoDBTableType,
  FirstStepTokenDataType,
  AssetPropertyKey
};
