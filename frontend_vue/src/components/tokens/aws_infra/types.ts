type S3ObjectType = {
  object_path: string;
};

type S3BucketType = {
  bucket_name: string;
  objects: S3ObjectType[] | [];
  off_inventory: boolean;
};

type SQSQueueType = {
  sqs_queue_name: string;
  off_inventory: boolean;
};

type SSMParameterType = {
  ssm_parameter_name: string;
  off_inventory: boolean;
};

type SecretsManagerSecretType = {
  secret_name: string;
  off_inventory: boolean;
};

type DynamoDBTableType = {
  table_name: string;
  table_items: string[];
  off_inventory: boolean;
};

type AssetsTypes = {
  S3Bucket?: S3BucketType[] | null;
  SQSQueue?: SQSQueueType[] | null;
  SSMParameter?: SSMParameterType[] | null;
  SecretsManagerSecret?: SecretsManagerSecretType[] | null;
  DynamoDBTable?: DynamoDBTableType[] | null;
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

type AssetDataTypeWithoutS3Object = Exclude<AssetDataType, S3ObjectType>;

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
  AssetDataTypeWithoutS3Object
};
