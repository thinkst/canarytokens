<template>
  <div class="p-40 bg-grey-50 rounded-xl">
    <div class="flex justify-between mb-24">
      <div>
        <SelectAddAsset
          @select-option="(assetKey) => handleAddNewAsset(assetKey)"
        />
      </div>
      <div class="flex items-center gap-8 text-grey-500">
        View:
        <button
          type="button"
          :class="{ 'text-green-500': viewType === VIEW_TYPE.LIST }"
          @click="handleSelectViewType(VIEW_TYPE.LIST)"
        >
          List
        </button>
        |
        <button
          type="button"
          :class="{ 'text-green-500': viewType === VIEW_TYPE.GRID }"
          @click="handleSelectViewType(VIEW_TYPE.GRID)"
        >
          Grid
        </button>
      </div>
    </div>
    <div class="min-h-[3rem]">
      <!-- Filters -->
      <div
        v-if="!numberSelectedAssets"
        class="flex flex-col items-center justify-between w-full gap-24 md:flex-row"
      >
        <ul class="flex flex-row flex-wrap gap-8 list-none justify-left">
          <FilterButton
            id="filterAll"
            category="All"
            category-type="Assets"
            :selected="!filterValue"
            :high-contrast="true"
            @click="filterValue = ''"
          />
          <li
            v-for="(_assetValues, assetKey) in assetSamples"
            :key="assetKey"
          >
            <FilterButton
              :category="ASSET_LABEL[assetKey]"
              category-type="Assets"
              :high-contrast="true"
              :selected="filterValue === assetKey"
              @click="handleFilterList(assetKey as keyof typeof ASSET_TYPE)"
            />
          </li>
        </ul>
      </div>
      <!-- Bulk select actions -->
      <div
        v-if="numberSelectedAssets"
        class="bg-grey-100 rounded-xl px-24 py-8 flex flex-row w-fit gap-8"
      >
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
      <section
        v-if="showSection(assetKey as keyof typeof ASSET_TYPE)"
        :id="`section-${assetKey}`"
        class="asset-section"
      >
        <h1 class="mb-16 mt-40 uppercase">{{ ASSET_LABEL[assetKey] }}</h1>
        <div
          :class="[
            {
              'grid grid-col-1 gap-8 auto-rows-fr': viewType === VIEW_TYPE.LIST,
            },
            {
              'grid gap-8 grid-cols-2 md:grid-cols-3 lg:grid-cols-5 2xl:grid-cols-6 auto-rows-fr':
                viewType === VIEW_TYPE.GRID,
            },
          ]"
        >
          <TransitionGroup name="list">
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
                handleRemoveAsset(
                  assetKey,
                  assetSamples[assetKey],
                  index,
                  false
                )
              "
            />
          </TransitionGroup>
          <ButtonAddAsset
            :asset-type="ASSET_LABEL[assetKey]"
            @add-asset="handleAddNewAsset(assetKey)"
          />
        </div>
      </section>
    </template>
  </div>
  <div class="flex justify-center mt-24">
    <BaseButton @click="handleSavePlan">Save Plan</BaseButton>
  </div>
</template>

<script setup lang="ts">
import { ref, provide, onMounted } from 'vue';
import type { Ref } from 'vue';
import { useModal } from 'vue-final-modal';
import { generateDataChoice } from '@/api/main';
// import type {
//   S3BucketType,
//   S3ObjectType,
//   SQSQueueType,
//   SSMParameterType,
//   SecretsManagerSecretType,
//   DynamoDBTableType,
// } from '@/components/tokens/aws_infra/types';
import FilterButton from '@/components/ui/FilterButton.vue';
import AssetCard from '@/components/tokens/aws_infra/plan_generator/AssetCard.vue';
import {
  ASSET_LABEL,
  ASSET_TYPE,
  ASSET_DATA,
} from '@/components/tokens/aws_infra/constants.ts';
import ModalAsset from '@/components/tokens/aws_infra/plan_generator/ModalAsset.vue';
import ModalDelete from '@/components/tokens/aws_infra/plan_generator/ModalDeleteAsset.vue';
import ButtonAddAsset from '@/components/tokens/aws_infra/plan_generator/ButtonAddAsset.vue';
import SelectAddAsset from '@/components/tokens/aws_infra/plan_generator/SelectAddAsset.vue';
import useMultiselectAssets from '@/components/tokens/aws_infra/plan_generator/useMultiselectAssets.ts';

type ViewTypeValue = (typeof VIEW_TYPE)[keyof typeof VIEW_TYPE];

const VIEW_TYPE = {
  GRID: 'gridView',
  LIST: 'listView',
} as const;

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

const viewType: Ref<ViewTypeValue> = ref(VIEW_TYPE.GRID);
const isLoading = ref(false);
const isErrorMessage = ref('');
const filterValue = ref('');
const {
  isActiveSelected,
  numberSelectedAssets,
  handleRemoveAllSelected,
  handleSelectAsset,
  resetSelectedAssetObj,
} = useMultiselectAssets(assetSamples);

provide('viewType', viewType);

onMounted(() => {
  resetSelectedAssetObj();
});

function handleSelectViewType(
  value: (typeof VIEW_TYPE)[keyof typeof VIEW_TYPE]
) {
  viewType.value = value;
}

function handleFilterList(assetType: keyof typeof ASSET_TYPE) {
  filterValue.value = assetType;
}

function showSection(assetType: keyof typeof ASSET_TYPE) {
  return filterValue.value === assetType || filterValue.value === '';
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

async function handleAddNewAsset(assetType: any) {
  const newAssetFields = () => {
    switch (assetType) {
      case ASSET_TYPE.S3BUCKET:
        return ASSET_DATA[ASSET_TYPE.S3BUCKET];
      case ASSET_TYPE.SQSQUEUE:
        return ASSET_DATA[ASSET_TYPE.SQSQUEUE];
      case ASSET_TYPE.SSMPARAMETER:
        return ASSET_DATA[ASSET_TYPE.SSMPARAMETER];
      case ASSET_TYPE.SECRETMANAGERSECRET:
        return ASSET_DATA[ASSET_TYPE.SECRETMANAGERSECRET];
      case ASSET_TYPE.DYNAMODBTABLE:
        return ASSET_DATA[ASSET_TYPE.DYNAMODBTABLE];
      default:
        return {};
    }
  };

  const newAssetValues = { ...newAssetFields() };

  async function getAssetRandomData() {
    isLoading.value = true;

    try {
      const results = await Promise.all(
        Object.keys(newAssetFields()).map(async (key) => {
          if (Array.isArray(newAssetValues[key])) return null;

          const res = await generateDataChoice(assetType);
          if (!res.result) {
            throw new Error(res.message);
          }
          return { key, value: res.proposed_data };
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
  handleSaveAsset(newAssetValues, assetType, -1);
  // scroll to section
  location.href = `#section-${assetType}`;
  // const section = document.getElementById(`section-${assetType}`);
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
