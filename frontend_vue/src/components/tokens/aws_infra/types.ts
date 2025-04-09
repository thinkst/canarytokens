type S3ObjectType = {
  object_path: string;
};

type S3BucketType = {
  bucket_name: string;
  objects: S3ObjectType[];
};

type SQSQueueType = {
  queue_name: string;
  message_count: number;
};

type SSMParameterType = {
  ssm_parameter_name: string;
  ssm_parameter_value: string;
};

type SecretsManagerSecretType = {
  secretsmanager_secret_name: string;
  secretsmanager_secret_value: string;
};

type DynamoDBTableType = {
  dynamodb_name: string;
  dynamodb_partition_key: string;
  dynamodb_row_count: number;
};

type AssetsTypes = {
  S3Bucket: S3BucketType[];
  // SQSQueue: SQSQueue[];
  // SSMParameter: SSMParameter[];
  // SecretsManagerSecret: SecretsManagerSecret[];
  // DynamoDBTable: DynamoDBTable[];
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
