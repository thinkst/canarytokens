<template>
  <BaseModal
    :title="`${assetLabel} Decoys`"
    :has-close-button="true"
    class="flex flex-row items-stretch"
  >
    <!-- Back Button-->
    <template #header-btn-left>
      <button
        v-if="showAssetDetails"
        type="button"
        :aria-label="`Back`"
        class="w-24 h-24 text-sm duration-150 bg-transparent border border-solid rounded-full hover:text-white text-grey-300 border-grey-300 hover:bg-green-600 hover:border-green-300"
        @click="handleCancelButton"
      >
        <font-awesome-icon
          icon="angle-left"
          aria-hidden="true"
        />
        <span class="fa-sr-only">Back</span>
      </button>
    </template>
    <div
      v-if="!showAssetDetails"
      class="flex flex-col mb-8"
    >
      <p class="text-center mb-16">
        {{ subtitle }}
      </p>
      <BaseButton
        v-if="!showAssetDetails"
        :loading="isLoading"
        :disabled="isMaxAssetsReached"
        class="self-end"
        variant="text"
        icon="plus"
        @click="handleAddNewAsset()"
      >
        New {{ assetLabel }} Decoy
      </BaseButton>
    </div>
    <!-- Asset List -->
    <BaseMessageBox
      v-if="isMaxAssetsReached && !showAssetDetails"
      variant="warning"
      class="mb-16"
      >You have reached the maximum of {{ MAX_DECOY_ASSETS }} decoys for
      {{ assetLabel }}.
    </BaseMessageBox>
    <BaseMessageBox
      v-if="isErrorMessage"
      variant="danger"
      class="mb-16"
      >{{ errorMessageMapper(isErrorMessage) }}
    </BaseMessageBox>
    <ModalAssetContentList
      v-if="!showAssetDetails"
      :asset-type="props.assetType"
      :asset-data="currentAssetData"
      @show-asset-details="
        (selectedItem, index) => handleShowAssetDetails(selectedItem, index)
      "
      @delete-asset="
        (index) => {
          handleDeleteAsset(index);
        }
      "
    />
    <!-- Asset Details -->
    <ModalAssetContentItem
      v-else
      :asset-type="props.assetType"
      :asset-data="removeManageInfo(currentAssetDetails.assetData)"
      :trigger-submit="triggerSubmit"
      :trigger-cancel="triggerCancel"
      @update-asset="
        (values) => {
          handleUpdateAsset(values);
        }
      "
      @update-temporary-asset="
        (values) => {
          handleUpdateTemporaryAsset(values);
        }
      "
    />
    <template #footer>
      <BaseButton
        v-if="!showAssetDetails"
        variant="grey"
        @click="handleCloseModal"
      >
        Close
      </BaseButton>
      <BaseButton
        v-if="showAssetDetails"
        variant="grey"
        @click="handleCancelButton"
      >
        Cancel
      </BaseButton>
      <BaseButton
        v-if="showAssetDetails"
        variant="primary"
        @click="handleSaveButton"
      >
        Save
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, nextTick, computed } from 'vue';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';
import type { ComputedRef } from 'vue';
import type { AssetData } from '../types';
import {
  getAssetLabel,
  getAssetDefaultValues,
} from '@/components/tokens/aws_infra/plan_generator/assetService.ts';
import { useGenerateAssetName } from '@/components/tokens/aws_infra/plan_generator/useGenerateAssetName.ts';
import ModalAssetContentList from './ModalAssetContentList.vue';
import ModalAssetContentItem from './ModalAssetContentItem.vue';
import { errorMessageMapper } from '@/utils/errorMessageMapper.ts';
import { setTempAssetsFields } from '@/components/tokens/aws_infra/plan_generator/planTempService.ts';

const MAX_DECOY_ASSETS = 10;

const props = defineProps<{
  assetType: AssetTypesEnum;
  assetData: ComputedRef<AssetData[] | [] | null>;
  closeModal: () => void;
}>();

const emit = defineEmits([
  'update-asset',
  'delete-asset',
  'add-asset',
  'update-temporary-asset',
]);
const showAssetDetails = ref(false);
const currentAssetDetails = ref({
  assetType: '' as AssetTypesEnum,
  assetData: {} as AssetData,
  index: -1,
});

const triggerSubmit = ref(false);
const triggerCancel = ref(false);
const isLoading = ref(false);
const isErrorMessage = ref('');

const currentAssetData = computed(() => {
  return props.assetData?.value ?? props.assetData;
});

const isEmptyAssetData = computed(
  () =>
    Array.isArray(currentAssetData.value) && currentAssetData.value.length === 0
);

const isMaxAssetsReached = computed(
  () =>
    Array.isArray(currentAssetData.value) &&
    currentAssetData.value.length >= MAX_DECOY_ASSETS
);

const assetLabel = computed(() => getAssetLabel(props.assetType));

const subtitle = computed(() => {
  return !isEmptyAssetData.value
    ? `We generated ${assetLabel.value} names based on your current deployment.`
    : `You can add new decoys to your ${assetLabel.value}.`;
});

function handleShowAssetDetails(selectedItem: AssetData, index: number) {
  isErrorMessage.value = '';
  showAssetDetails.value = true;
  currentAssetDetails.value = {
    assetType: props.assetType,
    assetData: selectedItem,
    index: index,
  };
}

function removeManageInfo(assetData: any) {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { off_inventory, ...rest } = assetData;
  return rest;
}

function handleUpdateAsset(values: any) {
  currentAssetDetails.value.assetData = values;
  emit('update-asset', currentAssetDetails.value);
  showAssetDetails.value = false;
}

function handleUpdateTemporaryAsset(values: AssetData) {
  setTempAssetsFields({
    ...currentAssetDetails.value,
    assetData: values,
  });
}

async function handleAddNewAsset() {
  if (isLoading.value) return;
  const newAssetFields = () => getAssetDefaultValues(props.assetType);

  const newAssetValues: Record<string, any> = { ...newAssetFields() };

  async function getAssetRandomData() {
    isLoading.value = true;
    isErrorMessage.value = '';

    try {
      const results = await Promise.all(
        Object.keys(newAssetFields()).map(async (key) => {
          if (Array.isArray(newAssetValues[key])) return null;
          if (key === 'off_inventory') return { key, value: false };

          const {
            handleGenerateName,
            isGenerateNameError,
            isGenerateNameLoading,
            generatedName,
          } = useGenerateAssetName(props.assetType, key);

          isLoading.value = isGenerateNameLoading.value;
          await handleGenerateName();
          isErrorMessage.value = isGenerateNameError.value;
          return { key, value: generatedName.value };
        })
      );

      results.forEach((result) => {
        if (result) {
          newAssetValues[result.key] = result.value;
        }
      });

      if (isErrorMessage.value) return null;
      emit('add-asset', newAssetValues);
    } catch (err: any) {
      if (err.response.status === 429) {
        isErrorMessage.value =
          err.response.data.message ||
          'You have reached your limit for AI-generated decoy names. You can continue with manual setup.';
        return;
      }
      isErrorMessage.value = err.response.data.message || 'An error occurred';
    } finally {
      isLoading.value = false;
    }
  }

  await getAssetRandomData();
}

function handleDeleteAsset(index: any) {
  isErrorMessage.value = '';
  emit('delete-asset', index);
}

function handleCloseModal() {
  props.closeModal();
}

function handleSaveButton() {
  triggerSubmit.value = true;
  nextTick(() => {
    triggerSubmit.value = false;
  });
}

function handleCancelButton() {
  triggerCancel.value = true;
  isErrorMessage.value = '';
  nextTick(() => {
    triggerCancel.value = false;
  });
}
</script>

<style lang="scss" scoped></style>
