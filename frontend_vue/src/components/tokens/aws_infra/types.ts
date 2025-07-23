type S3BucketData = {
  bucket_name: string;
  objects: string[];
  off_inventory?: boolean;
};

type SQSQueueData = {
  sqs_queue_name: string;
  off_inventory: boolean;
};

type SSMParameterData = {
  ssm_parameter_name: string;
  off_inventory: boolean;
};

type SecretsManagerSecretData = {
  secret_name: string;
  off_inventory: boolean;
};

type DynamoDBTableData = {
  table_name: string;
  table_items: string[];
  off_inventory: boolean;
};

type ProposedAWSInfraTokenPlanData = {
  S3Bucket?: S3BucketData[] | null;
  SQSQueue?: SQSQueueData[] | null;
  SSMParameter?: SSMParameterData[] | null;
  SecretsManagerSecret?: SecretsManagerSecretData[] | null;
  DynamoDBTable?: DynamoDBTableData[] | null;
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
  role_name?: string;
  external_id?: string;
};

export type {
  AssetData,
  S3BucketData,
  SQSQueueData,
  SSMParameterData,
  SecretsManagerSecretData,
  DynamoDBTableData,
  TokenSetupData,
  ProposedAWSInfraTokenPlanData,
};
