<template>
  <div class="flex flex-row justify-between my-16">
    <div class="flex flex-row gap-8 items-center">
      <img
        :src="iconURL()"
        :alt="`icon ${getLabel(props.assetKey)}`"
        class="h-[2rem] w-[2rem]"
      />
      <legend class="flex flex-col">
        <span class="text-grey-500">{{ getLabel(props.assetKey) }}</span>
        <span v-if="isObjectArray">{{
          getLabel(itemKey as keyof typeof ASSET_LABEL)
        }}</span>
      </legend>
    </div>
    <BaseButton
      type="button"
      variant="text"
      icon="plus"
      :loading="isLoading"
      @click="handleAddItem"
    >
      Add Decoy
    </BaseButton>
  </div>
  <BaseMessageBox
    v-if="isErrorMessage"
    variant="danger"
    >{{ isErrorMessage }}
  </BaseMessageBox>
  <AssetFormPagination :fields="props.fields">
    <div
      v-for="(field, fieldIndex) in fields"
      :key="fieldIndex"
      class="object_item pl-24"
    >
      <template v-if="isObjectArray">
        <div
          v-for="(_propertyValue, propertyKey) in field.value"
          :key="propertyKey"
        >
          <AssetTextField
            :id="`${props.assetKey}.${fieldIndex}.${propertyKey}`"
            :value="field.value[propertyKey]"
            :label="getLabel(propertyKey as any)"
            :field-type="itemKey"
            variant="small"
            :icon="`aws_infra_icons/${props.assetKey}.svg`"
            :hide-label="true"
            :has-remove="true"
            :asset-type="props.assetType"
            @handle-remove-instance="remove(fieldIndex)"
          />
        </div>
      </template>

      <template v-else>
        <AssetTextField
          :id="`${props.assetKey}.${fieldIndex}`"
          :value="field.value"
          :label="getLabel(props.assetKey as any)"
          :field-type="props.assetKey"
          variant="small"
          :icon="`aws_infra_icons/${props.assetKey}.svg`"
          :hide-label="true"
          :has-remove="true"
          :asset-type="props.assetType"
          @handle-remove-instance="remove(fieldIndex)"
        />
      </template>
    </div>
  </AssetFormPagination>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import {
  ASSET_LABEL,
  AssetTypesEnum,
  ASSET_TYPE_OBJECT,
} from '@/components/tokens/aws_infra/constants.ts';
import getImageUrl from '@/utils/getImageUrl';
import type { AssetDataType } from '../types';
import { useGenerateAssetName } from '@/components/tokens/aws_infra/plan_generator/useGenerateAssetName.ts';
import AssetFormPagination from '@/components/tokens/aws_infra/plan_generator/AssetFormPagination.vue';
import AssetTextField from '@/components/tokens/aws_infra/plan_generator/AssetTextField.vue';

const props = defineProps<{
  assetType: AssetTypesEnum;
  assetKey: keyof AssetDataType;
  fields: any;
  prepend: (value: any) => void;
  remove: (value: number) => void;
}>();

const isLoading = ref(false);
const isErrorMessage = ref('');

const isObjectArray = computed(() => {
  return ASSET_TYPE_OBJECT.includes(props.assetKey);
});

const itemKey = computed(() => {
  return props.fields.length > 0 ? Object.keys(props.fields[0].value)[0] : '';
});

function iconURL() {
  return getImageUrl(`aws_infra_icons/${props.assetKey}.svg`);
}

function getLabel(key: keyof typeof ASSET_LABEL) {
  return ASSET_LABEL[key];
}

async function handleAddItem() {
  isLoading.value = true;
  isErrorMessage.value = '';

  const {
    handleGenerateName,
    isGenerateNameError,
    isGenerateNameLoading,
    generatedName,
  } = useGenerateAssetName(props.assetType, itemKey.value);

  isLoading.value = isGenerateNameLoading.value;
  await handleGenerateName();
  isErrorMessage.value = isGenerateNameError.value;
  if (isErrorMessage.value) {
    isLoading.value = false;
    return;
  }
  if (isObjectArray.value) {
    props.prepend({ [itemKey.value]: generatedName.value });
  } else {
    props.prepend(generatedName.value);
  }
  isLoading.value = false;
}
</script>

<style></style>
