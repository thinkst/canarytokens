// Utils just to serve the static Plan Preview
// Remove this file when the Plan will be merged
import { ref } from 'vue';
import type { ProposedAWSInfraTokenPlanType } from '@/components/tokens/aws_infra/types.ts';

export function generateDataChoice() {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        result: 'true',
        message: '',
        proposed_data: 'Lorem ipsum data',
      });
    }, 200);
  });
}

export const assetsExample = ref<ProposedAWSInfraTokenPlanType>({
  S3Bucket: [
    {
      bucket_name: 'decoy-bucket-1',
      objects: [
        { object_path: 'foo/bar/object1' },
        { object_path: 'foo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-2-test-for-a-very-long-name',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-3',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-4',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-5',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-5',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-7',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-8',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-9',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
  ],
  SQSQueue: [
    {
      queue_name: 'decoy-queue-1',
      message_count: 5,
      off_inventory: false,
    },
    {
      queue_name: 'decoy-queue-2',
      message_count: 5,
      off_inventory: false,
    },
    {
      queue_name: 'decoy-queue-3',
      message_count: 5,
      off_inventory: false,
    },
    {
      queue_name: 'decoy-queue-4',
      message_count: 5,
      off_inventory: false,
    },
    {
      queue_name: 'decoy-queue-5',
      message_count: 5,
      off_inventory: false,
    },
    {
      queue_name: 'decoy-queue-6',
      message_count: 5,
      off_inventory: false,
    },
    {
      queue_name: 'decoy-queue-7',
      message_count: 5,
      off_inventory: false,
    },
    {
      queue_name: 'decoy-queue-8',
      message_count: 5,
      off_inventory: false,
    },
  ],
  SSMParameter: [
    {
      ssm_parameter_name: 'decoy-ssm-param-1',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-2',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-3',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-4',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-5',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-6',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-7',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-8',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
  ],
  SecretsManagerSecret: [
    {
      secretsmanager_secret_name: 'decoy-secretsmanager-secret-1',
      secretsmanager_secret_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      secretsmanager_secret_name: 'decoy-secretsmanager-secret-2',
      secretsmanager_secret_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      secretsmanager_secret_name: 'decoy-secretsmanager-secret-3',
      secretsmanager_secret_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
  ],
  DynamoDBTable: [
    {
      dynamodb_name: 'decoy-ssm-param-1',
      dynamodb_partition_key: 'username but very long',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
    {
      dynamodb_name: 'decoy-ssm-param-1-very-long-name',
      dynamodb_partition_key: 'username',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
    {
      dynamodb_name: 'decoy-ssm-param-22',
      dynamodb_partition_key: 'username but very long',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
    {
      dynamodb_name: 'decoy-ssm-param-3-very-long-name',
      dynamodb_partition_key: 'username',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
    {
      dynamodb_name: 'decoy-ssm-param-2',
      dynamodb_partition_key: 'username but very long',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
    {
      dynamodb_name: 'decoy-ssm-param-2-very-long-name',
      dynamodb_partition_key: 'username',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
    {
      dynamodb_name: 'decoy-ssm-param-5',
      dynamodb_partition_key: 'username but very long',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
    {
      dynamodb_name: 'decoy-ssm-param-55-very-long-name',
      dynamodb_partition_key: 'username',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
  ],
});

export const assetsWithEmptySQSQueue = ref<ProposedAWSInfraTokenPlanType>({
  S3Bucket: [
    {
      bucket_name: 'decoy-bucket-1',
      objects: [
        { object_path: 'foo/bar/object1' },
        { object_path: 'foo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-2-test-for-a-very-long-name',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-3',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-4',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-5',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-5',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-7',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-8',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-9',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: false,
    },
  ],
  SQSQueue: null,
  SSMParameter: [
    {
      ssm_parameter_name: 'decoy-ssm-param-1',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-2',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-3',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-4',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-5',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-6',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-7',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-8',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
  ],
  SecretsManagerSecret: [
    {
      secretsmanager_secret_name: 'decoy-secretsmanager-secret-1',
      secretsmanager_secret_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      secretsmanager_secret_name: 'decoy-secretsmanager-secret-2',
      secretsmanager_secret_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
    {
      secretsmanager_secret_name: 'decoy-secretsmanager-secret-3',
      secretsmanager_secret_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
  ],
  DynamoDBTable: [
    {
      dynamodb_name: 'decoy-ssm-param-1',
      dynamodb_partition_key: 'username but very long',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
    {
      dynamodb_name: 'decoy-ssm-param-1-very-long-name',
      dynamodb_partition_key: 'username',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
    {
      dynamodb_name: 'decoy-ssm-param-22',
      dynamodb_partition_key: 'username but very long',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
    {
      dynamodb_name: 'decoy-ssm-param-3-very-long-name',
      dynamodb_partition_key: 'username',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
    {
      dynamodb_name: 'decoy-ssm-param-2',
      dynamodb_partition_key: 'username but very long',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
    {
      dynamodb_name: 'decoy-ssm-param-2-very-long-name',
      dynamodb_partition_key: 'username',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
    {
      dynamodb_name: 'decoy-ssm-param-5',
      dynamodb_partition_key: 'username but very long',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
    {
      dynamodb_name: 'decoy-ssm-param-55-very-long-name',
      dynamodb_partition_key: 'username',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
  ],
});

export const assetsManageExample = ref<ProposedAWSInfraTokenPlanType>({
  S3Bucket: [
    {
      bucket_name: 'decoy-bucket-1',
      objects: [
        { object_path: 'foo/bar/object1' },
        { object_path: 'foo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-2-test-for-a-very-long-name',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: true,
    },
  ],
  SQSQueue: [
    {
      queue_name: 'decoy-queue-1',
      message_count: 5,
      off_inventory: false,
    },
    {
      queue_name: 'decoy-queue-2',
      message_count: 5,
      off_inventory: false,
    },
  ],
  SSMParameter: [
    {
      ssm_parameter_name: 'decoy-ssm-param-1',
      ssm_parameter_value: 'some_fake_looking_api_key',
      off_inventory: false,
    },
  ],
  SecretsManagerSecret: [
    {
      secretsmanager_secret_name: 'decoy-secretsmanager-secret-1',
      secretsmanager_secret_value: 'some_fake_looking_api_key',
      off_inventory: true,
    },
  ],
  DynamoDBTable: [
    {
      dynamodb_name: 'decoy-ssm-param-2-very-long-name',
      dynamodb_partition_key: 'username',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
  ],
});

export const assetInitialEmptyParameter = ref<ProposedAWSInfraTokenPlanType>({
  S3Bucket: [
    {
      bucket_name: 'decoy-bucket-1',
      objects: [
        { object_path: 'foo/bar/object1' },
        { object_path: 'foo/baz/object2' },
      ],
      off_inventory: false,
    },
    {
      bucket_name: 'decoy-bucket-2-test-for-a-very-long-name',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
      off_inventory: true,
    },
  ],
  SQSQueue: [
    {
      queue_name: 'decoy-queue-1',
      message_count: 5,
      off_inventory: false,
    },
    {
      queue_name: 'decoy-queue-2',
      message_count: 5,
      off_inventory: false,
    },
  ],
  SecretsManagerSecret: [
    {
      secretsmanager_secret_name: 'decoy-secretsmanager-secret-1',
      secretsmanager_secret_value: 'some_fake_looking_api_key',
      off_inventory: true,
    },
  ],
  DynamoDBTable: [
    {
      dynamodb_name: 'decoy-ssm-param-2-very-long-name',
      dynamodb_partition_key: 'username',
      dynamodb_row_count: 10,
      off_inventory: false,
    },
  ],
});
