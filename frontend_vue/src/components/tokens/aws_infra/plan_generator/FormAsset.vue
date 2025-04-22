<template>
  <Form
    ref="formAssetRef"
    class="w-full"
    :initial-values="initialValues"
    :validation-schema="props.validationSchema"
    @submit="onSubmit"
    @invalid-submit="onInvalidSubmit"
  >
    <div
      v-for="(value, key) in initialValues"
      :key="key"
    >
      <template v-if="Array.isArray(value)">
        <FieldArray
          v-slot="{ fields, push, remove }"
          name="objects"
        >
          <button
            type="button"
            @click="push({ object_path: '' })"
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
                :label="ASSET_LABEL[propertyKey]"
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
          :label="ASSET_LABEL[key]"
        />
      </template>
    </div>
  </Form>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import type { Ref } from 'vue';
import { Form, FieldArray } from 'vee-validate';
import type { GenericObject } from 'vee-validate';
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
  ASSET_LABEL,
} from '@/components/tokens/aws_infra/constants.ts';
import AssetTextField from '@/components/tokens/aws_infra/plan_generator/AssetTextField.vue';

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
  validationSchema: any;
  triggerSubmit: boolean;
}>();

const emits = defineEmits(['update-asset', 'invalid-submit']);
const initialValues = ref({});
const formAssetRef: Ref<HTMLFormElement | null> = ref(null);

function onSubmit(values: GenericObject) {
  emits('update-asset', values);
}

function onInvalidSubmit(values: any) {
  emits('invalid-submit', values);
}

function programaticSubmit() {
  if (formAssetRef.value) {
    formAssetRef.value.$el.requestSubmit();
  }
}

const newAssetValues = computed(() => {
  switch (props.assetType) {
    case ASSET_TYPE.S3BUCKET:
      return ASSET_DATA[ASSET_TYPE.S3BUCKET];
    case ASSET_TYPE.SQSQUEUE:
      return ASSET_DATA[ASSET_TYPE.SQSQUEUE];
    case ASSET_TYPE.SSMPARAMETER:
      return ASSET_DATA[ASSET_TYPE.SSMPARAMETER];
    case ASSET_TYPE.SECRETMANAGERSECRET:
      return ASSET_DATA[ASSET_TYPE.SECRETMANAGERSECRET];
    case ASSET_TYPE.DYNAMODBTABLE:
      return ASSET_DATA[ASSET_TYPE.DYNAMODBTABLE];
    default:
      return { newKey: '' };
  }
});

watch(
  () => props.assetData,
  (newAssetData) => {
    if (newAssetData && Object.keys(newAssetData).length > 0) {
      initialValues.value = { ...newAssetData };
    } else {
      initialValues.value = newAssetValues.value;
    }
  },
  { immediate: true }
);

watch(
  () => props.triggerSubmit,
  (newVal) => {
    if (newVal === true) return programaticSubmit();
  },
  { immediate: true }
);
</script>
