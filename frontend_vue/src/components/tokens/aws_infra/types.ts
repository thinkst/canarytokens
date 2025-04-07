type S3Object = {
  object_path: string;
};

type S3Bucket = {
  bucket_name: string;
  objects: S3Object[];
};

type SQSQueue = {
  queue_name: string;
  message_count: number;
};

type SSMParameter = {
  ssm_parameter_name: string;
  ssm_parameter_value: string;
};

type SecretsManagerSecret = {
  secretsmanager_secret_name: string;
  secretsmanager_secret_value: string;
};

type DynamoDBTable = {
  dynamodb_name: string;
  dynamodb_partition_key: string;
  dynamodb_row_count: number;
};

type Assets = {
  S3Bucket: S3Bucket[];
  SQSQueue: SQSQueue[];
  SSMParameter: SSMParameter[];
  SecretsManagerSecret: SecretsManagerSecret[];
  DynamoDBTable: DynamoDBTable[];
};


export type { S3Bucket, S3Object, SQSQueue, SSMParameter, SecretsManagerSecret, DynamoDBTable, Assets };