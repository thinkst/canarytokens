<!-- eslint-disable vue/no-unused-vars -->
<template>
  <BaseModal
    :title="modalTitle"
    :has-close-button="true"
  >
    <Form
      class="w-full"
      :initial-values="initialValues"
      :validation-schema="validationSchema"
      @submit="handleUpdateAsset"
      @invalid-submit="handleInvalidSubmit"
    >
      <div
        v-for="(value, key, index) in initialValues"
        :key="key"
      >
        <template v-if="Array.isArray(value)">
          <FieldArray
            v-slot="{ fields, push, remove }"
            name="objects"
          >
            <button
              type="button"
              @click="push(newAsset)"
            >
              Add
            </button>
            <fieldset
              v-for="(field, fieldIndex) in fields"
              :key="fieldIndex"
            >
              <template
                v-for="(_propertyValue, propertyKey) in field.value"
                :key="propertyKey"
              >
                <AssetTextField
                  :id="`${key}.${fieldIndex}.${propertyKey}`"
                  v-model="field.value[propertyKey]"
                  :label="ASSET_DATA_LABEL[propertyKey]"
                />
              </template>
              <button
                type="button"
                @click="remove(fieldIndex)"
              >
                Remove
              </button>
            </fieldset>
          </FieldArray>
        </template>
        <template v-else>
          <AssetTextField
            :id="key"
            v-model="initialValues[key]"
            :label="ASSET_DATA_LABEL[key]"
          />
        </template>
      </div>

      <div class="flex flex-16 gap-16">
        <BaseButton
          variant="grey"
          @click="handleCancel()"
          >Cancel</BaseButton
        >
        <BaseButton
          variant="primary"
          type="submit"
          >Save</BaseButton
        >
      </div>
    </Form>
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

const emits = defineEmits(['updateAsset']);
const initialValues = ref({});

onMounted(() => {
  initialValues.value = { ...props.assetData };
});

const isExistingAsset = computed(() => {
  return Object.keys(props.assetData).length > 0;
});

const modalTitle = computed(() => {
  return isExistingAsset.value
    ? `Edit ${props.assetType}`
    : `Add new ${props.assetType}`;
});

const newAsset = computed(() => {
  switch (props.assetType) {
    case ASSET_TYPE.S3BUCKET:
      return ASSET_DATA[ASSET_TYPE.S3BUCKET_OBJECT];
    default:
      return { newKey: '' };
  }
});

function handleUpdateAsset(values: any) {
  console.log(values, 'values');
  // initialValues.value;
  emits('updateAsset', values);
}

function handleInvalidSubmit() {
  console.log('invalid biaaatch');
}

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
