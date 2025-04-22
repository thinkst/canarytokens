<!-- eslint-disable vue/no-unused-vars -->
<template>
  <BaseModal
    :title="modalTitle"
    :has-close-button="true"
  >
    <FormEditAsset
      :asset-type="props.assetType"
      :asset-data="props.assetData"
      :close-modal="props.closeModal"
      :validation-schema="validationSchema"
      :trigger-submit="triggerSubmit"
      @update-asset="handleUpdateAsset"
    />
    <template #footer>
      <BaseButton
        variant="grey"
        @click="handleCancel()"
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
import { computed, ref, onMounted } from 'vue';
import { Form, FieldArray } from 'vee-validate';
import type {
  S3BucketType,
  S3ObjectType,
  SQSQueueType,
  SSMParameterType,
  SecretsManagerSecretType,
  DynamoDBTableType,
} from '../types';
import {
  ASSET_TYPE,
  ASSET_DATA,
  ASSET_DATA_LABEL,
} from '@/components/tokens/aws_infra/constants.ts';
import AssetTextField from '@/components/tokens/aws_infra/plan_generator/AssetTextField.vue';
import { S3Bucket_schema, Default_schema } from './assetValidators';
import FormEditAsset from './FormEditAsset.vue';

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

const emits = defineEmits(['update-asset']);
const triggerSubmit = ref(false);

const isExistingAsset = computed(() => {
  return Object.keys(props.assetData).length > 0;
});

const modalTitle = computed(() => {
  return isExistingAsset.value
    ? `Edit ${props.assetType}`
    : `Add new ${props.assetType}`;
});

// const newAsset = computed(() => {
//   switch (props.assetType) {
//     case ASSET_TYPE.S3BUCKET:
//       return ASSET_DATA[ASSET_TYPE.S3BUCKET_OBJECT];
//     default:
//       return { newKey: '' };
//   }
// });

function handleUpdateAsset(values: any) {
  console.log(values, 'values');
  // // initialValues.value;
  emits('update-asset', values);
}

function handleSubmit() {
  triggerSubmit.value = true;
}

// function handleInvalidSubmit() {
//   console.log('invalid biaaatch');
// }

function handleCancel() {
  props.closeModal();
}

const validationSchema = computed(() => {
  switch (props.assetType) {
    case ASSET_TYPE.S3BUCKET:
      return S3Bucket_schema;
    default:
      return Default_schema;
  }
});
</script>
