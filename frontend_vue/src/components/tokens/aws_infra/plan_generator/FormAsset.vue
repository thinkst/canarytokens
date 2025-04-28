<template>
  <Form
    ref="formAssetRef"
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
          v-slot="{ fields, prepend, remove }"
          name="objects"
        >
          <FormObjects
            :asset-key="key"
            object-key="object_path"
            :fields="fields"
            :prepend="prepend"
            :remove="remove"
          />
        </FieldArray>
      </template>
      <template v-else>
        <AssetTextField
          :id="key"
          v-model="initialValues[key]"
          :label="getLabel(key)"
          :asset-type="key"
        />
      </template>
    </div>
  </Form>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import type { Ref } from 'vue';
import { Form, FieldArray } from 'vee-validate';
import type { GenericObject } from 'vee-validate';

import type {
  S3BucketType,
  SQSQueueType,
  SSMParameterType,
  SecretsManagerSecretType,
  DynamoDBTableType,
} from '../types';
import {
  ASSET_TYPE,
  ASSET_LABEL,
} from '@/components/tokens/aws_infra/constants.ts';
import AssetTextField from '@/components/tokens/aws_infra/plan_generator/AssetTextField.vue';
import FormObjects from '@/components/tokens/aws_infra/plan_generator/FormObjects.vue';

type AssetConstKeyType = keyof typeof ASSET_TYPE;
type AssetConstValuesType = (typeof ASSET_TYPE)[AssetConstKeyType];
type AssetType =
  | S3BucketType
  | SQSQueueType
  | SSMParameterType
  | SecretsManagerSecretType
  | DynamoDBTableType;

const props = defineProps<{
  assetType: AssetConstValuesType;
  assetData: AssetType;
  validationSchema: any;
  triggerSubmit: boolean;
  triggerCancel: boolean;
  closeModal: () => void;
}>();

const emits = defineEmits(['update-asset', 'invalid-submit']);
const initialValues = ref({});
const formAssetRef: Ref<HTMLFormElement | null> = ref(null);
const tempFields: Ref<AssetType | []> = ref([]);

onMounted(() => {
  tempFields.value = { ...props.assetData };
  const firstInput = formAssetRef.value?.$el.getElementsByTagName('input')[0];
  firstInput.focus();
});

function onSubmit(values: GenericObject) {
  emits('update-asset', values);
  props.closeModal();
}

function onInvalidSubmit(values: any) {
  emits('invalid-submit', values);
}

function handleProgramaticSubmit() {
  if (formAssetRef.value) {
    formAssetRef.value.$el.requestSubmit();
  }
}

function handleRestoreFields() {
  emits('update-asset', tempFields);
}

function getLabel(key: keyof typeof ASSET_LABEL) {
  return ASSET_LABEL[key];
}

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
    if (newVal === true) return handleProgramaticSubmit();
  },
  { immediate: true }
);

watch(
  () => props.triggerCancel,
  (newVal) => {
    if (newVal === true) return handleRestoreFields();
  },
  { immediate: true }
);
</script>
