type S3ObjectType = {
  object_path: string;
};

type S3BucketType = {
  bucket_name: string;
  objects: S3ObjectType[];
  offInventory: boolean;
};

type SQSQueueType = {
  queue_name: string;
  message_count: number;
  offInventory: boolean;
};

type SSMParameterType = {
  ssm_parameter_name: string;
  ssm_parameter_value: string;
  offInventory: boolean;
};

type SecretsManagerSecretType = {
  secretsmanager_secret_name: string;
  secretsmanager_secret_value: string;
  offInventory: boolean;
};

type DynamoDBTableType = {
  dynamodb_name: string;
  dynamodb_partition_key: string;
  dynamodb_row_count: number;
  offInventory: boolean;
};

type AssetsTypes = {
  S3Bucket: S3BucketType[];
  SQSQueue: SQSQueueType[];
  SSMParameter: SSMParameterType[];
  SecretsManagerSecret: SecretsManagerSecretType[];
  DynamoDBTable: DynamoDBTableType[];
};

type PlanValueTypes = {
  assets: AssetsTypes;
};

export type {
  AssetsTypes,
  S3BucketType,
  S3ObjectType,
  SQSQueueType,
  SSMParameterType,
  SecretsManagerSecretType,
  DynamoDBTableType,
  PlanValueTypes,
};
