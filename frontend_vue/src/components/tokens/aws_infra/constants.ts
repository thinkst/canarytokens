export const INSTANCE_TYPE = {
  S3BUCKET: 'S3Bucket',
  S3BUCKET_NAME: 'bucket_name',
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

export const AWS_REGIONS = [
  { value: 'us-east-1', label: 'US East (N. Virginia)' },
  { value: 'us-east-2', label: 'US East (Ohio)' },
  { value: 'us-west-1', label: 'US West (N. California)' },
  { value: 'us-west-2', label: 'US West (Oregon)' },
  { value: 'ca-central-1', label: 'Canada (Central)' },
  { value: 'ca-west-1', label: 'Canada West (Calgary)' },
  { value: 'eu-north-1', label: 'EU (Stockholm)' },
  { value: 'eu-west-3', label: 'EU (Paris)' },
  { value: 'eu-west-2', label: 'EU (London)' },
  { value: 'eu-west-1', label: 'EU (Ireland)' },
  { value: 'eu-central-1', label: 'EU (Frankfurt)' },
  { value: 'eu-south-1', label: 'EU (Milan)' },
  { value: 'eu-south-2', label: 'EU (Spain)' },
  { value: 'eu-central-2', label: 'EU (Zurich)' },
  { value: 'ap-south-1', label: 'Asia Pacific (Mumbai)' },
  { value: 'ap-northeast-1', label: 'Asia Pacific (Tokyo)' },
  { value: 'ap-northeast-2', label: 'Asia Pacific (Seoul)' },
  { value: 'ap-northeast-3', label: 'Asia Pacific (Osaka-Local)' },
  { value: 'ap-southeast-1', label: 'Asia Pacific (Singapore)' },
  { value: 'ap-southeast-2', label: 'Asia Pacific (Sydney)' },
  { value: 'ap-southeast-3', label: 'Asia Pacific (Jakarta)' },
  { value: 'ap-east-1', label: 'Asia Pacific (Hong Kong) SAR' },
  { value: 'sa-east-1', label: 'South America (São Paulo)' },
  { value: 'cn-north-1', label: 'China (Beijing)' },
  { value: 'cn-northwest-1', label: 'China (Ningxia)' },
  { value: 'us-gov-east-1', label: 'AWS GovCloud (US-East)' },
  { value: 'us-gov-west-1', label: 'AWS GovCloud (US-West)' },
  { value: 'us-isob-east-1', label: 'AWS Secret Region (US ISOB East Ohio)' },
  {
    value: 'us-iso-east-1',
    label: 'AWS Top Secret-East Region (US ISO East Virginia)',
  },
  {
    value: 'us-iso-west-1',
    label: 'AWS Top Secret-West Region (US ISO West Colorado)',
  },
  { value: 'me-south-1', label: 'Middle East (Bahrain)' },
  { value: 'af-south-1', label: 'Africa (Cape Town)' },
  { value: 'me-central-1', label: 'Middle East (United Arab Emirates)' },
  { value: 'ap-south-2', label: 'Asia Pacific (Hyderabad)' },
  { value: 'ap-southeast-4', label: 'Asia Pacific (Melbourne)' },
  { value: 'il-central-1', label: 'Israel (Tel Aviv)' },
  { value: 'ap-southeast-5', label: 'Asia Pacific (Malaysia)' },
  { value: 'ap-southeast-7', label: 'Asia Pacific (Thailand)' },
  { value: 'mx-central-1', label: 'Mexico (Central)' },
];
