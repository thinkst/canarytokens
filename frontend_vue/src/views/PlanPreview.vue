<template>
  <div class="p-40 bg-grey-50 rounded-xl">
    <div class="flex justify-between mb-24">
      <div>
        <SelectAddAsset
          @select-option="
            (assetKey) => handleOpenAssetModal(null, assetKey, -1)
          "
        />
      </div>
      <div class="flex items-center gap-8 text-grey-500">
        View:
        <button
          type="button"
          :class="{ 'text-green-500': viewType === VIEW_TYPE.LIST }"
          @click="selectViewType(VIEW_TYPE.LIST)"
        >
          List
        </button>
        |
        <button
          type="button"
          :class="{ 'text-green-500': viewType === VIEW_TYPE.GRID }"
          @click="selectViewType(VIEW_TYPE.GRID)"
        >
          Grid
        </button>
      </div>
    </div>
    <div
      v-if="numberSelectedAssets"
      class="min-h-[3rem]"
    >
      <!-- Add Filter!! -->
      <div class="bg-grey-100 rounded-xl px-24 py-8 flex flex-row w-fit gap-8">
        <span>{{ numberSelectedAssets }} assets selected: </span>
        <button
          type="button"
          class="font-semibold hover:text-red"
          @click="handleRemoveAsset(null, null, 0, true)"
        >
          Delete All
        </button>
        <button
          type="button"
          class="ml-8 font-semibold hover:text-green-500"
          @click="resetSelectedAssetObj"
        >
          Unselect All
        </button>
      </div>
    </div>

    <template
      v-for="(assetValues, assetKey) in assetSamples"
      :key="assetKey"
    >
      <h1 class="mb-16 mt-40 uppercase">{{ ASSET_LABEL[assetKey] }}</h1>
      <div
        :class="[
          { 'grid grid-col-1 gap-8 auto-rows-fr': viewType === VIEW_TYPE.LIST },
          {
            'grid gap-8 grid-cols-2 md:grid-cols-3 lg:grid-cols-5 2xl:grid-cols-6 auto-rows-fr':
              viewType === VIEW_TYPE.GRID,
          },
        ]"
      >
        <!-- <TransitionGroup name="list"> -->
        <AssetCard
          v-for="(asset, index) of assetValues"
          :key="`${assetKey}-${index}`"
          :asset-type="assetKey"
          :asset-data="asset"
          :is-active-selected="isActiveSelected"
          @open-asset="handleOpenAssetModal(asset, assetKey, index)"
          @select-asset="
            (isSelected) => handleSelectAsset(isSelected, assetKey, index)
          "
          @delete-asset="
            handleRemoveAsset(assetKey, assetSamples[assetKey], index, false)
          "
        />
        <!-- </TransitionGroup> -->
        <ButtonAddAsset
          :asset-type="ASSET_LABEL[assetKey]"
          @add-asset="handleOpenAssetModal(null, assetKey, -1)"
        />
      </div>
    </template>
  </div>
  <div class="flex justify-center mt-24">
    <BaseButton @click="handleSavePlan">Save Plan</BaseButton>
  </div>
</template>

<script setup lang="ts">
import { ref, provide, onMounted, computed } from 'vue';
import type { Ref } from 'vue';
import { useModal } from 'vue-final-modal';
import AssetCard from '@/components/tokens/aws_infra/plan_generator/AssetCard.vue';
import { ASSET_LABEL } from '@/components/tokens/aws_infra/constants.ts';
import ModalAsset from '@/components/tokens/aws_infra/plan_generator/ModalAsset.vue';
import ModalDelete from '@/components/tokens/aws_infra/plan_generator/ModalDeleteAsset.vue';
import ButtonAddAsset from '@/components/tokens/aws_infra/plan_generator/ButtonAddAsset.vue';
import SelectAddAsset from '@/components/tokens/aws_infra/plan_generator/SelectAddAsset.vue';

type ViewTypeValue = (typeof VIEW_TYPE)[keyof typeof VIEW_TYPE];

const VIEW_TYPE = {
  GRID: 'gridView',
  LIST: 'listView',
} as const;

const viewType: Ref<ViewTypeValue> = ref(VIEW_TYPE.GRID);
const selectedAssets: Ref<any[]> = ref([]);
const isActiveSelected = ref(false);

provide('viewType', viewType);

onMounted(() => {
  resetSelectedAssetObj();
});

const numberSelectedAssets = computed(() => {
  let selectedItems = 0;

  selectedAssets.value.forEach((obj) => {
    const indexArray = Object.values(obj)[0];

    if (Array.isArray(indexArray)) {
      selectedItems += indexArray.length;
    }
  });

  return selectedItems;
});

function resetSelectedAssetObj() {
  isActiveSelected.value = false;
  selectedAssets.value = Object.keys(assetSamples.value).map((key) => {
    return { [key]: [] };
  });
}

function selectViewType(value: (typeof VIEW_TYPE)[keyof typeof VIEW_TYPE]) {
  viewType.value = value;
}
function handleSelectAsset(
  isSelected: boolean,
  assetKey: string,
  index: number
) {
  const assetObject = selectedAssets.value.find((item) => assetKey in item);

  if (isSelected) {
    isActiveSelected.value = true;
    if (
      assetObject &&
      Array.isArray(assetObject[assetKey]) &&
      !assetObject[assetKey].includes(index)
    ) {
      assetObject[assetKey].push(index);
    }
  }

  if (!isSelected) {
    if (assetObject && Array.isArray(assetObject[assetKey])) {
      assetObject[assetKey] = assetObject[assetKey].filter(
        (item) => item !== index
      );
    }
  }
}

function handleRemoveAllSelected() {
  const updatedAssets = { ...assetSamples.value };

  selectedAssets.value.forEach((assetGroup) => {
    const assetKey = Object.keys(assetGroup)[0];
    const indicesToRemove = assetGroup[assetKey];
    // Order indexes in descending order
    // To avoid weird shifting in index order during the loop
    const sortedIndicesToRemove = [...indicesToRemove].sort((a, b) => b - a);

    if (
      updatedAssets[assetKey as keyof typeof assetSamples.value] &&
      Array.isArray(indicesToRemove)
    ) {
      sortedIndicesToRemove.forEach((index) => {
        if (index >= 0 && index < updatedAssets[assetKey].length) {
          updatedAssets[assetKey].splice(index, 1);
        }
      });
    }
  });

  assetSamples.value = updatedAssets;
  resetSelectedAssetObj();
}

function handleRemoveAsset(
  assetType: any,
  list: any,
  index: number,
  isBulkDelete: boolean
) {
  const { open, close } = useModal({
    component: ModalDelete,
    attrs: {
      assetType: assetType,
      isBulkDelete: isBulkDelete,
      closeModal: () => {
        close();
      },
      onDeleteConfirmed: () => {
        !isBulkDelete ? list.splice(index, 1) : handleRemoveAllSelected();
      },
    },
  });
  open();
}

function handleOpenAssetModal(assetData: any, assetType: any, index: number) {
  const { open, close } = useModal({
    component: ModalAsset,
    attrs: {
      assetType: assetType,
      assetData: assetData,
      closeModal: () => {
        close();
      },
      'onUpdate-asset': (newValues) => {
        handleSaveAsset(newValues, assetType, index);
      },
    },
  });
  open();
}

function handleSaveAsset(
  newValues: any,
  assetType: keyof typeof assetSamples.value,
  index: number
) {
  if (index === -1) {
    assetSamples.value[assetType].push(newValues);
  } else {
    assetSamples.value[assetType][index] = newValues;
  }
}

function handleSavePlan() {
  alert(JSON.stringify(assetSamples.value));
}

const assetSamples = ref<{
  S3Bucket: { bucket_name: string; objects: { object_path: string }[] }[];
  SQSQueue: { queue_name: string; message_count: number }[];
  SSMParameter: { ssm_parameter_name: string; ssm_parameter_value: string }[];
  SecretsManagerSecret: {
    secretsmanager_secret_name: string;
    secretsmanager_secret_value: string;
  }[];
  DynamoDBTable: {
    dynamodb_name: string;
    dynamodb_partition_key: string;
    dynamodb_row_count: number;
  }[];
}>({
  S3Bucket: [
    {
      bucket_name: 'decoy-bucket-1',
      objects: [
        { object_path: 'foo/bar/object1' },
        { object_path: 'foo/baz/object2' },
      ],
    },
    {
      bucket_name: 'decoy-bucket-2-test-for-a-very-long-name',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
    },
    {
      bucket_name: 'decoy-bucket-3',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
    },
    {
      bucket_name: 'decoy-bucket-3',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
    },
    {
      bucket_name: 'decoy-bucket-3',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
    },
    {
      bucket_name: 'decoy-bucket-3',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
    },
    {
      bucket_name: 'decoy-bucket-3',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
    },
    {
      bucket_name: 'decoy-bucket-3',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
    },
    {
      bucket_name: 'decoy-bucket-4',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/baz/object2' },
      ],
    },
  ],
  SQSQueue: [
    {
      queue_name: 'decoy-queue-1',
      message_count: 5,
    },
    {
      queue_name: 'decoy-queue-1',
      message_count: 5,
    },
    {
      queue_name: 'decoy-queue-1',
      message_count: 5,
    },
    {
      queue_name: 'decoy-queue-1',
      message_count: 5,
    },
    {
      queue_name: 'decoy-queue-1',
      message_count: 5,
    },
    {
      queue_name: 'decoy-queue-1',
      message_count: 5,
    },
    {
      queue_name: 'decoy-queue-1',
      message_count: 5,
    },
    {
      queue_name: 'decoy-queue-1',
      message_count: 5,
    },
  ],
  SSMParameter: [
    {
      ssm_parameter_name: 'decoy-ssm-param-1',
      ssm_parameter_value: 'some_fake_looking_api_key',
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-1',
      ssm_parameter_value: 'some_fake_looking_api_key',
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-1',
      ssm_parameter_value: 'some_fake_looking_api_key',
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-1',
      ssm_parameter_value: 'some_fake_looking_api_key',
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-1',
      ssm_parameter_value: 'some_fake_looking_api_key',
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-1',
      ssm_parameter_value: 'some_fake_looking_api_key',
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-1',
      ssm_parameter_value: 'some_fake_looking_api_key',
    },
    {
      ssm_parameter_name: 'decoy-ssm-param-1',
      ssm_parameter_value: 'some_fake_looking_api_key',
    },
  ],
  SecretsManagerSecret: [
    {
      secretsmanager_secret_name: 'decoy-secretsmanager-secret-1',
      secretsmanager_secret_value: 'some_fake_looking_api_key',
    },
    {
      secretsmanager_secret_name: 'decoy-secretsmanager-secret-1',
      secretsmanager_secret_value: 'some_fake_looking_api_key',
    },
    {
      secretsmanager_secret_name: 'decoy-secretsmanager-secret-1',
      secretsmanager_secret_value: 'some_fake_looking_api_key',
    },
  ],
  DynamoDBTable: [
    {
      dynamodb_name: 'decoy-ssm-param-1',
      dynamodb_partition_key: 'username but very long',
      dynamodb_row_count: 10,
    },
    {
      dynamodb_name: 'decoy-ssm-param-1-very-long-name',
      dynamodb_partition_key: 'username',
      dynamodb_row_count: 10,
    },
    {
      dynamodb_name: 'decoy-ssm-param-1',
      dynamodb_partition_key: 'username but very long',
      dynamodb_row_count: 10,
    },
    {
      dynamodb_name: 'decoy-ssm-param-1-very-long-name',
      dynamodb_partition_key: 'username',
      dynamodb_row_count: 10,
    },
    {
      dynamodb_name: 'decoy-ssm-param-1',
      dynamodb_partition_key: 'username but very long',
      dynamodb_row_count: 10,
    },
    {
      dynamodb_name: 'decoy-ssm-param-1-very-long-name',
      dynamodb_partition_key: 'username',
      dynamodb_row_count: 10,
    },
    {
      dynamodb_name: 'decoy-ssm-param-1',
      dynamodb_partition_key: 'username but very long',
      dynamodb_row_count: 10,
    },
    {
      dynamodb_name: 'decoy-ssm-param-1-very-long-name',
      dynamodb_partition_key: 'username',
      dynamodb_row_count: 10,
    },
  ],
});
</script>

<style>
.list-enter-active,
.list-leave-active {
  transition: all 0.2s ease;
  transition-delay: 0.2s;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}
</style>
