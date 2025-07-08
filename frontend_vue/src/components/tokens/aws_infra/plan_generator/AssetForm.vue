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
          :name="key"
        >
          <AssetFormArray
            :asset-type="props.assetType"
            :asset-key="key"
            :fields="fields"
            :prepend="prepend"
            :remove="remove"
          />
        </FieldArray>
      </template>
      <template v-else>
        <AssetTextField
          :id="key"
          :value="initialValues[key]"
          :label="getFieldLabel(props.assetType, key)"
          :field-type="key"
          :asset-type="props.assetType"
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
import type { AssetData } from '../types';
import {
  AssetTypesEnum,
} from '@/components/tokens/aws_infra/constants.ts';
import AssetTextField from '@/components/tokens/aws_infra/plan_generator/AssetTextField.vue';
import { getFieldLabel } from '@/components/tokens/aws_infra/plan_generator/assetService.ts';
import AssetFormArray from '@/components/tokens/aws_infra/plan_generator/AssetFormArray.vue';

const props = defineProps<{
  assetType: AssetTypesEnum;
  assetData: AssetData;
  validationSchema: any;
  triggerSubmit: boolean;
  triggerCancel: boolean;
}>();

const emits = defineEmits(['update-asset', 'invalid-submit']);
const initialValues = ref({});
const formAssetRef: Ref<HTMLFormElement | null> = ref(null);
const tempFields: Ref<AssetData | []> = ref([]);

onMounted(() => {
  tempFields.value = { ...props.assetData };
  const firstInput = formAssetRef.value?.$el.getElementsByTagName('input')[0];
  firstInput.focus();
});

function onSubmit(values: GenericObject) {
  emits('update-asset', values);
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
    console.log('triggerSubmit', newVal);
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
