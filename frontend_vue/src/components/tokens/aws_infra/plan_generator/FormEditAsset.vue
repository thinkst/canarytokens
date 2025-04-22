<template>
  <Form
    ref="editAssetForm"
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
  </Form>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue';
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
const editAssetForm: Ref<HTMLFormElement | null> = ref(null);

function onSubmit(values: any) {
  emits('update-asset', values);
}

function onInvalidSubmit(values: any) {
  console.log('onInvalidSubmit');
  emits('invalid-submit', values);
}

function programaticSubmit() {
  if (editAssetForm.value) {
    editAssetForm.value.$el.requestSubmit();
  }
}

const newAsset = computed(() => {
  switch (props.assetType) {
    case ASSET_TYPE.S3BUCKET:
      return ASSET_DATA[ASSET_TYPE.S3BUCKET_OBJECT];
    default:
      return { newKey: '' };
  }
});

watch(
  () => props.assetData,
  (newAssetData) => {
    initialValues.value = { ...newAssetData };
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
