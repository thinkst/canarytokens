export const INSTANCE_TYPE = {
  S3BUCKET: 'S3Bucket',
  S3BUCKET_OBJECT: 'object_path',
  //   SQSQUEUE: 'SQSQueue',
  //   SSMPARAMETER: 'SSMParameter',
  //   SECRETMANAGERSECRET: 'SecretsManagerSecret',
  //   DYNAMODBTABLE: 'DynamoDBTable',
} as const;

export const INSTANCE_DATA = {
  [INSTANCE_TYPE.S3BUCKET]: {
    bucket_name: '',
    objects: [],
  },
  [INSTANCE_TYPE.S3BUCKET_OBJECT]: {
    object_path: '',
  },
  //   [INSTANCE_TYPE.SQSQUEUE]: {
  //     queue_name: '',
  //     message_count: null,
  //   },
  //   [INSTANCE_TYPE.SSMPARAMETER]: {
  //     ssm_parameter_name: '',
  //     ssm_parameter_value: '',
  //   },
  //   [INSTANCE_TYPE.SECRETMANAGERSECRET]: {
  //     secretsmanager_secret_name: '',
  //     secretsmanager_secret_value: '',
  //   },
  //   [INSTANCE_TYPE.DYNAMODBTABLE]: {
  //     dynamodb_name: '',
  //     dynamodb_partition_key: '',
  //     dynamodb_row_count: '',
  //   },
};
