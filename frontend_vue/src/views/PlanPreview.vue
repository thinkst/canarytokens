<template>
  <div class="flex gap-8 mb-24">
    Select view:
    <button
      type="button"
      :class="{ 'text-green-500': viewType === VIEW_TYPE.LIST }"
      @click="selectViewType(VIEW_TYPE.LIST)"
    >
      List
    </button>
    <button
      type="button"
      :class="{ 'text-green-500': viewType === VIEW_TYPE.GRID }"
      @click="selectViewType(VIEW_TYPE.GRID)"
    >
      Grid
    </button>
  </div>

  <h1 class="mb-8">S3 Buckets</h1>
  <div
    :class="[
      { 'grid grid-col-1 gap-8': viewType === VIEW_TYPE.LIST },
      {
        'grid gap-8 grid-cols-2 md:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6':
          viewType === VIEW_TYPE.GRID,
      },
    ]"
  >
    <TransitionGroup name="list">
      <AssetCard
        v-for="(asset, index) of assetSamples.S3Bucket"
        :key="asset"
        :asset-type="ASSET_TYPE.S3BUCKET"
        :asset-data="asset"
        @open-asset="handleOpenAsset(asset, ASSET_TYPE.S3BUCKET)"
        @select-asset="(isSelected) => handleSelectAsset(isSelected, asset)"
        @delete-asset="
          handleRemoveAsset(ASSET_TYPE.S3BUCKET, assetSamples.S3Bucket, index)
        "
      />
    </TransitionGroup>
  </div>

  <h1 class="mt-24 mb-16">DynamoDBTable</h1>
  <div
    :class="[
      { 'grid grid-col-1 gap-8': viewType === VIEW_TYPE.LIST },
      {
        'grid gap-8 grid-cols-2 md:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6':
          viewType === VIEW_TYPE.GRID,
      },
    ]"
  >
    <TransitionGroup name="list">
      <AssetCard
        v-for="(asset, index) of assetSamples.DynamoDBTable"
        :key="asset"
        :asset-type="ASSET_TYPE.DYNAMODBTABLE"
        :asset-data="asset"
        @open-asset="handleOpenAsset(asset, ASSET_TYPE.DYNAMODBTABLE)"
        @select-asset="(isSelected) => handleSelectAsset(isSelected, asset)"
        @delete-asset="
          handleRemoveAsset(
            ASSET_TYPE.DYNAMODBTABLE,
            assetSamples.DynamoDBTable,
            index
          )
        "
      />
    </TransitionGroup>
  </div>

  <h1 class="mt-24 mb-16">Secrets Manager Secret</h1>
  <div
    :class="[
      { 'grid grid-col-1 gap-8': viewType === VIEW_TYPE.LIST },
      {
        'grid gap-8 grid-cols-2 md:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6':
          viewType === VIEW_TYPE.GRID,
      },
    ]"
  >
    <TransitionGroup name="list">
      <AssetCard
        v-for="(asset, index) of assetSamples.SecretsManagerSecret"
        :key="asset"
        :asset-type="ASSET_TYPE.SECRETMANAGERSECRET"
        :asset-data="asset"
        @open-asset="handleOpenAsset(asset, ASSET_TYPE.SECRETMANAGERSECRET)"
        @select-asset="(isSelected) => handleSelectAsset(isSelected, asset)"
        @delete-asset="
          handleRemoveAsset(
            ASSET_TYPE.SECRETMANAGERSECRET,
            assetSamples.SecretsManagerSecret,
            index
          )
        "
      />
    </TransitionGroup>
  </div>

  <h1 class="mt-24 mb-16">SQSQueue</h1>
  <div
    :class="[
      { 'grid grid-col-1 gap-8': viewType === VIEW_TYPE.LIST },
      {
        'grid gap-8 grid-cols-2 md:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6':
          viewType === VIEW_TYPE.GRID,
      },
    ]"
  >
    <TransitionGroup name="list">
      <AssetCard
        v-for="(asset, index) of assetSamples.SQSQueue"
        :key="asset"
        :asset-type="ASSET_TYPE.SQSQUEUE"
        :asset-data="asset"
        @open-asset="handleOpenAsset(asset, ASSET_TYPE.SQSQUEUE)"
        @select-asset="(isSelected) => handleSelectAsset(isSelected, asset)"
        @delete-asset="
          handleRemoveAsset(ASSET_TYPE.SQSQUEUE, assetSamples.SQSQueue, index)
        "
      />
    </TransitionGroup>
  </div>

  <h1 class="mt-24 mb-16">SSMParameter</h1>
  <div
    :class="[
      { 'grid grid-col-1 gap-8': viewType === VIEW_TYPE.LIST },
      {
        'grid gap-8 grid-cols-2 md:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6':
          viewType === VIEW_TYPE.GRID,
      },
    ]"
  >
    <TransitionGroup name="list">
      <AssetCard
        v-for="(asset, index) of assetSamples.SSMParameter"
        :key="asset"
        :asset-type="ASSET_TYPE.SSMPARAMETER"
        :asset-data="asset"
        @open-asset="handleOpenAsset(asset, ASSET_TYPE.SSMPARAMETER)"
        @select-asset="(isSelected) => handleSelectAsset(isSelected, asset)"
        @delete-asset="
          handleRemoveAsset(
            ASSET_TYPE.SSMPARAMETER,
            assetSamples.SSMParameter,
            index
          )
        "
      />
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { ref, provide } from 'vue';
import type { Ref } from 'vue';
import { useModal } from 'vue-final-modal';
import AssetCard from '@/components/tokens/aws_infra/plan_generator/AssetCard.vue';
import { ASSET_TYPE } from '@/components/tokens/aws_infra/constants.ts';
import ModalAsset from '@/components/tokens/aws_infra/plan_generator/ModalAsset.vue';
import ModalDelete from '@/components/tokens/aws_infra/plan_generator/ModalDelete.vue';

type ViewTypeValue = (typeof VIEW_TYPE)[keyof typeof VIEW_TYPE];

const VIEW_TYPE = {
  GRID: 'gridView',
  LIST: 'listView',
} as const;

const viewType: Ref<ViewTypeValue> = ref(VIEW_TYPE.GRID);
const selectedAssets: Ref<any[]> = ref([]);

provide('viewType', viewType);

function selectViewType(value: (typeof VIEW_TYPE)[keyof typeof VIEW_TYPE]) {
  viewType.value = value;
}

function handleSelectAsset(isSelected: boolean, asset: any) {
  console.log(isSelected, asset);
}

function handleRemoveAsset(assetType: any, list: any, index: number) {
  const { open, close } = useModal({
    component: ModalDelete,
    attrs: {
      assetType: assetType,
      closeModal: () => {
        close();
      },
      onDeleteConfirmed: () => {
        list.splice(index, 1);
      },
    },
  });
  open();
}

function handleOpenAsset(assetData: any, assetType: any) {
  const { open } = useModal({
    component: ModalAsset,
    attrs: {
      assetType: assetType,
      assetData: assetData,
      closeModal: () => close(),
    },
  });
  open();
}

const assetSamples = ref({
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
