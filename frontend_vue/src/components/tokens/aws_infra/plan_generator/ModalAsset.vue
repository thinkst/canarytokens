<template>
  <BaseModal
    :title="`${props.assetType} Decoys`"
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
        @click="handleBackButton"
      >
        <font-awesome-icon
          icon="angle-left"
          aria-hidden="true"
        />
        <span class="fa-sr-only">Back</span>
      </button>
    </template>
    <!-- Content -->

    <BaseButton
      v-if="!showAssetDetails"
      :loading="isLoading"
      @click="handleAddNewAsset()"
    >
      Add new {{ props.assetType }}
    </BaseButton>
    <BaseMessageBox
      v-if="isErrorMessage"
      variant="danger"
      >{{ isErrorMessage }}
    </BaseMessageBox>
    <ModalAssetContentList
      v-if="!showAssetDetails"
      :asset-type="props.assetType"
      :asset-data="props.assetData"
      @show-asset-details="
        (selectedItem, index) => handleShowAssetDetails(selectedItem, index)
      "
      @delete-asset="
        (index) => {
          handleDeleteAsset(index);
        }
      "
    />
    <ModalAssetContentItem
      v-else
      :asset-type="props.assetType"
      :asset-data="removeManageInfo(selectedAssetDetails.assetData)"
      :trigger-submit="triggerSubmit"
      :trigger-cancel="triggerCancel"
      @update-asset="
        (values) => {
            handleUpdateAsset(values);
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
import { ref, nextTick } from 'vue';
import {
  ASSET_DATA,
  AssetTypesEnum,
} from '@/components/tokens/aws_infra/constants.ts';
import type { AssetDataTypeWithoutS3Object } from '../types';
import { useGenerateAssetName } from '@/components/tokens/aws_infra/plan_generator/useGenerateAssetName.ts';
import ModalAssetContentList from './ModalAssetContentList.vue';
import ModalAssetContentItem from './ModalAssetContentItem.vue';

const props = defineProps<{
  assetType: AssetTypesEnum;
  assetData: AssetDataTypeWithoutS3Object;
  closeModal: () => void;
}>();

const emit = defineEmits(['update-asset', 'delete-asset', 'add-asset']);

const showAssetDetails = ref(false);
const selectedAssetDetails = ref({
  assetType: '',
  assetData: {} as AssetDataTypeWithoutS3Object,
  index: -1,
});

const triggerSubmit = ref(false);
const triggerCancel = ref(false);
const isLoading = ref(false);
const isErrorMessage = ref('');

function handleShowAssetDetails(selectedItem: AssetDataTypeWithoutS3Object, index: number) {
  isErrorMessage.value = '';
  showAssetDetails.value = true;
  selectedAssetDetails.value = {
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
  selectedAssetDetails.value.assetData = values;
  emit('update-asset', selectedAssetDetails.value);
  showAssetDetails.value = false;
//   props.closeModal();
}

async function handleAddNewAsset() {
  const newAssetFields = () => {
    switch (props.assetType) {
      case AssetTypesEnum.S3BUCKET:
        return ASSET_DATA[AssetTypesEnum.S3BUCKET];
      case AssetTypesEnum.SQSQUEUE:
        return ASSET_DATA[AssetTypesEnum.SQSQUEUE];
      case AssetTypesEnum.SSMPARAMETER:
        return ASSET_DATA[AssetTypesEnum.SSMPARAMETER];
      case AssetTypesEnum.SECRETMANAGERSECRET:
        return ASSET_DATA[AssetTypesEnum.SECRETMANAGERSECRET];
      case AssetTypesEnum.DYNAMODBTABLE:
        return ASSET_DATA[AssetTypesEnum.DYNAMODBTABLE];
      default:
        return {};
    }
  };

  const newAssetValues: Record<string, any> = { ...newAssetFields() };

  async function getAssetRandomData() {
    isLoading.value = true;

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
    } catch (err: any) {
      isErrorMessage.value = err.message || 'An error occurred';
    } finally {
      isLoading.value = false;
    }
  }

  await getAssetRandomData();
  emit('add-asset', newAssetValues);
}

function handleDeleteAsset(index: any) {
  isErrorMessage.value = '';
  emit('delete-asset', index);
}


function handleCloseModal() {
  props.closeModal();
  showAssetDetails.value = false;
}

function handleSaveButton() {
  triggerSubmit.value = true;
//   showAssetDetails.value = false;
    nextTick(() => {
        triggerSubmit.value = false;
    });
}

function handleCancelButton() {
  triggerCancel.value = true;
  nextTick(() => {
    triggerCancel.value = false;
  });
}

function handleBackButton() {
  isErrorMessage.value = '';
  showAssetDetails.value = false;
}


</script>

<style lang="scss" scoped></style>
