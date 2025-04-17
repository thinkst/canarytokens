<template>
  <BaseModal
    :title="`Edit ${props.assetType}`"
    :has-close-button="true"
  >
    {{ props.assetData }}
  </BaseModal>
</template>

<script setup lang="ts">
import type {
  S3BucketType,
  S3ObjectType,
  SQSQueueType,
  SSMParameterType,
  SecretsManagerSecretType,
  DynamoDBTableType,
} from '../types';
import { ASSET_TYPE } from '@/components/tokens/aws_infra/constants.ts';

type AssetConstKeyType = keyof typeof ASSET_TYPE;
type AssetConstValuesType = (typeof ASSET_TYPE)[AssetConstKeyType];
type AssetType =
  | S3BucketType
  | S3ObjectType
  | SQSQueueType
  | SSMParameterType
  | SecretsManagerSecretType
  | DynamoDBTableType;

const props = defineProps<{
  assetType: AssetConstValuesType;
  assetData: AssetType;
  closeModal: () => void;
}>();
</script>
