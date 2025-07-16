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
      v-if="isErrorMessage"
      variant="danger"
      class="mb-16"
      >{{ isErrorMessage }}
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
import { ref, nextTick, computed } from 'vue';
import {
  ASSET_LABEL,
  AssetTypesEnum,
} from '@/components/tokens/aws_infra/constants.ts';
import type { ComputedRef } from 'vue';
import type {
  AssetTypes,
  DynamoDBTableType,
  SecretsManagerSecretType,
  SSMParameterType,
  SQSQueueType,
  S3BucketType,
} from '../types';
import { useGenerateAssetName } from '@/components/tokens/aws_infra/plan_generator/useGenerateAssetName.ts';
import ModalAssetContentList from './ModalAssetContentList.vue';
import ModalAssetContentItem from './ModalAssetContentItem.vue';

const props = defineProps<{
  assetType: AssetTypesEnum;
  assetData: ComputedRef<AssetTypes[] | [] | null>;
  closeModal: () => void;
}>();

const emit = defineEmits(['update-asset', 'delete-asset', 'add-asset']);

const currentAssetData = computed(() => {
  return props.assetData?.value ?? props.assetData;
});

const showAssetDetails = ref(false);
const selectedAssetDetails = ref({
  assetType: '',
  assetData: {} as AssetTypes,
  index: -1,
});

const triggerSubmit = ref(false);
const triggerCancel = ref(false);
const isLoading = ref(false);
const isErrorMessage = ref('');

function handleShowAssetDetails(selectedItem: AssetTypes, index: number) {
  isErrorMessage.value = '';
  showAssetDetails.value = true;
  selectedAssetDetails.value = {
    assetType: props.assetType,
    assetData: selectedItem,
    index: index,
  };
}

const isEmptyAssetData = computed(() => {
  if (
    Array.isArray(currentAssetData.value) &&
    currentAssetData.value.length === 0
  ) {
    return true;
  }
  return false;
});

const assetLabel = computed(() => ASSET_LABEL[props.assetType]);
const subtitle = computed(() => {
  return !isEmptyAssetData.value
    ? `We generated names for your ${assetLabel.value} is based on your current deployment.`
    : `You can add new decoys to your ${assetLabel.value} list.`;
});

function removeManageInfo(assetData: any) {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { off_inventory, ...rest } = assetData;
  return rest;
}

function handleUpdateAsset(values: any) {
  selectedAssetDetails.value.assetData = values;
  emit('update-asset', selectedAssetDetails.value);
  showAssetDetails.value = false;
}

async function handleAddNewAsset() {
  const newAssetFields = () => {
    switch (props.assetType) {
      case AssetTypesEnum.S3BUCKET:
        return {
          bucket_name: '',
          objects: [],
          off_inventory: false,
        } as S3BucketType;
      case AssetTypesEnum.SQSQUEUE:
        return {
          queue_name: '',
          message_count: null,
          off_inventory: false,
        } as SQSQueueType;
      case AssetTypesEnum.SSMPARAMETER:
        return {
          ssm_parameter_name: '',
          ssm_parameter_value: '',
          off_inventory: false,
        } as SSMParameterType;
      case AssetTypesEnum.SECRETMANAGERSECRET:
        return {
          secretsmanager_secret_name: '',
          secretsmanager_secret_value: '',
          off_inventory: false,
        } as SecretsManagerSecretType;
      case AssetTypesEnum.DYNAMODBTABLE:
        return {
          dynamodb_name: '',
          dynamodb_partition_key: '',
          dynamodb_row_count: null,
          off_inventory: false,
        } as DynamoDBTableType;
      default:
        return {};
    }
  };

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
      isErrorMessage.value = err.message || 'An error occurred';
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
  showAssetDetails.value = false;
}

function handleSaveButton() {
  triggerSubmit.value = true;
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
