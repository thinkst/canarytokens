<template>
  <div class="flex flex-row justify-between my-16">
    <div class="flex flex-row gap-8 items-center">
      <img
        :src="iconURL()"
        :alt="`icon ${getFieldLabel(props.assetType, props.assetKey)}`"
        class="h-[2rem] w-[2rem]"
      />
      <legend class="flex flex-col">
        <span class="text-grey-500">{{
          getFieldLabel(props.assetType, props.assetKey)
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
    >{{ errorMessageMapper(isErrorMessage) }}
  </BaseMessageBox>
  <AssetFormPagination :fields="props.fields">
    <div
      v-for="(field, fieldIndex) in fields"
      :key="fieldIndex"
      class="object_item pl-24"
    >
      <AssetTextField
        :id="`${props.assetKey}.${fieldIndex}`"
        :value="field.value"
        :label="getFieldLabel(props.assetType, props.assetKey as any)"
        :field-type="props.assetKey"
        variant="small"
        :icon="`aws_infra_icons/${props.assetKey}.svg`"
        :hide-label="true"
        :has-remove="true"
        :asset-type="props.assetType"
        @handle-remove-instance="remove(fieldIndex)"
      />
    </div>
  </AssetFormPagination>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';
import getImageUrl from '@/utils/getImageUrl';
import type { AssetData } from '../types';
import { getFieldLabel } from '@/components/tokens/aws_infra/plan_generator/assetService.ts';
import { useGenerateAssetName } from '@/components/tokens/aws_infra/plan_generator/useGenerateAssetName.ts';
import AssetFormPagination from '@/components/tokens/aws_infra/plan_generator/AssetFormPagination.vue';
import AssetTextField from '@/components/tokens/aws_infra/plan_generator/AssetTextField.vue';
import { errorMessageMapper } from '@/utils/errorMessageMapper.ts';

const props = defineProps<{
  assetType: AssetTypesEnum;
  assetKey: keyof AssetData;
  fields: any;
  parentAssetName: string;
  prepend: (value: any) => void;
  remove: (value: number) => void;
}>();

const isLoading = ref(false);
const isErrorMessage = ref('');

function iconURL() {
  return getImageUrl(`aws_infra_icons/${props.assetKey}.svg`);
}

async function handleAddItem() {
  if (isLoading.value) return;
  isLoading.value = true;
  isErrorMessage.value = '';

  const {
    handleGenerateName,
    isGenerateNameError,
    isGenerateNameLoading,
    generatedName,
  } = useGenerateAssetName(props.assetType, props.assetKey);

  isLoading.value = isGenerateNameLoading.value;
  await handleGenerateName(props.parentAssetName);
  isErrorMessage.value = isGenerateNameError.value;
  if (isErrorMessage.value) {
    isLoading.value = false;
    return;
  }
  props.prepend(generatedName.value);
  isLoading.value = false;
}
</script>

<style></style>
