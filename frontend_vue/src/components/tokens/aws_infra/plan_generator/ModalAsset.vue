<template>
  <BaseModal
    :title="`Edit ${props.assetType}`"
    :has-close-button="true"
    class="flex flex-row items-stretch"
    @keydown.enter="handleSubmit"
  >
    <div
      class="border bg-white rounded-2xl shadow-solid-shadow-grey border-grey-200 p-16 mx-24 my-16"
    >
      <FormAsset
        :asset-type="props.assetType"
        :asset-data="props.assetData"
        :close-modal="props.closeModal"
        :validation-schema="validationSchema"
        :trigger-submit="triggerSubmit"
        :trigger-cancel="triggerCancel"
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
import type { AssetDataType } from '../types';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';
import {
  S3Bucket_schema,
  SQSQueue_schema,
  SSMParameter_schema,
  SecretsManagerSecret_schema,
  DynamoDBTable_schema,
  Default_schema,
} from './assetValidators';
import FormAsset from './FormAsset.vue';

const props = defineProps<{
  assetType: AssetTypesEnum;
  assetData: AssetDataType;
  closeModal: () => void;
}>();

const emits = defineEmits(['update-asset']);
const triggerSubmit = ref(false);
const triggerCancel = ref(false);

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
    case AssetTypesEnum.S3BUCKET:
      return S3Bucket_schema;
    case AssetTypesEnum.SQSQUEUE:
      return SQSQueue_schema;
    case AssetTypesEnum.SSMPARAMETER:
      return SSMParameter_schema;
    case AssetTypesEnum.SECRETMANAGERSECRET:
      return SecretsManagerSecret_schema;
    case AssetTypesEnum.DYNAMODBTABLE:
      return DynamoDBTable_schema;
    default:
      return Default_schema;
  }
});
</script>
