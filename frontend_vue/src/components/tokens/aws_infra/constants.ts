export const ASSET_TYPE = {
  S3BUCKET: 'S3Bucket',
  S3BUCKET_OBJECT: 'object_path',
  SQSQUEUE: 'SQSQueue',
  SSMPARAMETER: 'SSMParameter',
  SECRETMANAGERSECRET: 'SecretsManagerSecret',
  DYNAMODBTABLE: 'DynamoDBTable',
} as const;

export const ASSET_DATA = {
  [ASSET_TYPE.S3BUCKET]: {
    bucket_name: '',
    objects: [],
  },
  [ASSET_TYPE.S3BUCKET_OBJECT]: {
    object_path: '',
  },
  [ASSET_TYPE.SQSQUEUE]: {
    queue_name: '',
    message_count: null,
  },
  [ASSET_TYPE.SSMPARAMETER]: {
    ssm_parameter_name: '',
    ssm_parameter_value: '',
  },
  [ASSET_TYPE.SECRETMANAGERSECRET]: {
    secretsmanager_secret_name: '',
    secretsmanager_secret_value: '',
  },
  [ASSET_TYPE.DYNAMODBTABLE]: {
    dynamodb_name: '',
    dynamodb_partition_key: '',
    dynamodb_row_count: '',
  },
};

export const ASSET_WITH_ICON = ['objects'];

export const ASSET_LABEL = {
  [ASSET_TYPE.S3BUCKET]: 'S3 Bucket',
  [ASSET_TYPE.SQSQUEUE]: 'SQS Queue',
  [ASSET_TYPE.SSMPARAMETER]: 'SSM Parameter',
  [ASSET_TYPE.SECRETMANAGERSECRET]: 'Secrets Manager Secret',
  [ASSET_TYPE.DYNAMODBTABLE]: 'Dynamo DB Table',
  dynamodb_row_count: 'Row Count',
  dynamodb_partition_key: 'Partition Key',
  dynamodb_name: 'Table Name',
  secretsmanager_secret_value: 'Secret Value',
  secretsmanager_secret_name: 'Secret Name',
  ssm_parameter_value: 'Parameter Value',
  ssm_parameter_name: 'Parameter Name',
  message_count: 'Message Count',
  queue_name: 'Queue Name',
  object_path: 'Object Path',
  bucket_name: 'S3 Bucket Name',
  objects: 'Objects',
};

// Main keys for the Asset Card
// to display close to the asset icon
export const ASSET_DATA_NAME = {
  [ASSET_TYPE.DYNAMODBTABLE]: 'dynamodb_name',
  [ASSET_TYPE.SECRETMANAGERSECRET]: 'secretsmanager_secret_name',
  [ASSET_TYPE.SSMPARAMETER]: 'ssm_parameter_name',
  [ASSET_TYPE.SQSQUEUE]: 'queue_name',
  [ASSET_TYPE.S3BUCKET]: 'bucket_name',
};
