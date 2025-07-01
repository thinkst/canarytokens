type S3ObjectType = {
  object_path: string;
};

type S3BucketType = {
  bucket_name: string;
  objects: S3ObjectType[] | [];
  off_inventory: boolean;
};

type SQSQueueType = {
  queue_name: string;
  message_count: number | null;
  off_inventory: boolean;
};

type SSMParameterType = {
  ssm_parameter_name: string;
  ssm_parameter_value: string;
  off_inventory: boolean;
};

type SecretsManagerSecretType = {
  secretsmanager_secret_name: string;
  secretsmanager_secret_value: string;
  off_inventory: boolean;
};

type DynamoDBTableType = {
  dynamodb_name: string;
  dynamodb_partition_key: string;
  dynamodb_row_count: number | null;
  off_inventory: boolean;
};

type AssetsTypes = {
  S3Bucket: S3BucketType[] | null;
  SQSQueue: SQSQueueType[] | null;
  SSMParameter: SSMParameterType[] | null;
  SecretsManagerSecret: SecretsManagerSecretType[] | null;
  DynamoDBTable: DynamoDBTableType[] | null;
};

type AssetDataType =
  | DynamoDBTableType
  | SecretsManagerSecretType
  | SSMParameterType
  | SQSQueueType
  | S3BucketType
  | S3ObjectType;

type PlanValueTypes = {
  assets: AssetsTypes;
};

type CurrentTokenDataType = {
  token: string;
  auth_token: string;
  proposed_plan: PlanValueTypes;
  code_snippet_command?: string;
};

export type {
  AssetDataType,
  AssetsTypes,
  S3BucketType,
  S3ObjectType,
  SQSQueueType,
  SSMParameterType,
  SecretsManagerSecretType,
  DynamoDBTableType,
  PlanValueTypes,
  CurrentTokenDataType,
};
