export const howToUse = [
  'Click the Quick Create link to deploy the CloudFormation stack in your AWS account. This creates a decoy S3 bucket, a CloudTrail trail, and an EventBridge rule that forwards access events to Canarytokens.',
  'Any access to the decoy bucket (list, get, put, delete) triggers an alert. Place references to the bucket name in internal documentation, config files, or wikis to catch unauthorized access.',
];
