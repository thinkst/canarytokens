<template>
  <form
    ref="formAssetRef"
    :initial-values="initialValues"
    :validation-schema="props.validationSchema"
    @submit="onSubmit"
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
            :parent-asset-name="parentAssetName"
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
  </form>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed, useTemplateRef } from 'vue';
import type { Ref } from 'vue';
import { FieldArray, useForm } from 'vee-validate';
import type { GenericObject } from 'vee-validate';
import type { AssetData } from '../types';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';
import AssetTextField from '@/components/tokens/aws_infra/plan_generator/AssetTextField.vue';
import {
  getFieldLabel,
  getAssetNameKey,
} from '@/components/tokens/aws_infra/plan_generator/assetService.ts';
import AssetFormArray from '@/components/tokens/aws_infra/plan_generator/AssetFormArray.vue';

const props = defineProps<{
  assetType: AssetTypesEnum;
  assetData: AssetData;
  validationSchema: any;
  triggerSubmit: boolean;
  triggerCancel: boolean;
}>();

const emit = defineEmits([
  'update-asset',
  'invalid-submit',
  'update-temporary-asset',
]);
const initialValues = ref({});
const formAssetRef: Ref<HTMLFormElement | null> =
  useTemplateRef('formAssetRef');

const { values, handleSubmit } = useForm({
  initialValues: props.assetData,
  validationSchema: props.validationSchema,
});

onMounted(() => {
  const firstInput = formAssetRef.value?.querySelector('input');
  firstInput?.focus();
});

const parentAssetName = computed((): string => {
  const assetNameKey = getAssetNameKey(props.assetType) as keyof AssetData;
  return String(props.assetData[assetNameKey]) || '';
});

function onSubmit(values: GenericObject) {
  handleSubmit(() => {
    emit('update-asset', values);
  })();
}

function handleProgramaticSubmit() {
  handleSubmit(onSubmit)();
}

function handleRestoreFields() {
  emit('update-asset', initialValues.value);
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

watch(
  values,
  (newValues) => {
    emit('update-temporary-asset', newValues);
  },
  { deep: true }
);
</script>
