<template>
  <BaseModal
    :title="modalTitle"
    :has-close-button="true"
    class="flex flex-row items-stretch"
  >
    <div
      class="border bg-white rounded-2xl shadow-solid-shadow-grey border-grey-200 p-16 mx-24 my-16"
    >
      <!-- @vue-expect-error: TS breaks for no reason on props.assetData even when type casted -->
      <FormAsset
        :asset-type="props.assetType"
        :asset-data="props.assetData"
        :close-modal="props.closeModal"
        :validation-schema="validationSchema"
        :trigger-submit="triggerSubmit"
        @update-asset="handleUpdateAsset"
        @invalid-submit="handleInvalidSubmit"
      />
    </div>

    <template #footer>
      <BaseButton
        variant="grey"
        @click="handleCancel"
        >Cancel</BaseButton
      >
      <BaseButton
        variant="primary"
        type="submit"
        @click="handleSubmit"
        >Save</BaseButton
      >
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import type {
  S3BucketType,
  S3ObjectType,
  SQSQueueType,
  SSMParameterType,
  SecretsManagerSecretType,
  DynamoDBTableType,
} from '../types';
import { ASSET_TYPE } from '@/components/tokens/aws_infra/constants.ts';
import {
  S3Bucket_schema,
  SQSQueue_schema,
  SSMParameter_schema,
  SecretsManagerSecret_schema,
  DynamoDBTable_schema,
  Default_schema,
} from './assetValidators';
import FormAsset from './FormAsset.vue';

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
  assetData: AssetType | null;
  closeModal: () => void;
}>();

const emits = defineEmits(['update-asset']);
const triggerSubmit = ref(false);
const triggerCancel = ref(false);

const isExistingAsset = computed(() => {
  return props.assetData && Object.keys(props.assetData).length > 0;
});

const modalTitle = computed(() => {
  return isExistingAsset.value
    ? `Edit ${props.assetType}`
    : `Add new ${props.assetType}`;
});

function handleUpdateAsset(values: any) {
  emits('update-asset', values);
}

function handleSubmit() {
  triggerSubmit.value = true;
}

function handleInvalidSubmit() {
  triggerSubmit.value = false;
}

function handleCancel() {
  triggerCancel.value = true;
  props.closeModal();
}

const validationSchema = computed(() => {
  switch (props.assetType) {
    case ASSET_TYPE.S3BUCKET:
      return S3Bucket_schema;
    case ASSET_TYPE.SQSQUEUE:
      return SQSQueue_schema;
    case ASSET_TYPE.SSMPARAMETER:
      return SSMParameter_schema;
    case ASSET_TYPE.SECRETMANAGERSECRET:
      return SecretsManagerSecret_schema;
    case ASSET_TYPE.DYNAMODBTABLE:
      return DynamoDBTable_schema;
    default:
      return Default_schema;
  }
});
</script>
