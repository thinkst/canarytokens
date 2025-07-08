<template>
  <ul class="flex flex-col gap-8">
  <AssetCard
    v-for="(asset, index) of props.assetData"
    :key="`${index}-${props.assetType}`"
    :asset-data="asset"
    :asset-type="assetType as AssetTypesEnum"
    view-type="listView"
    @show-asset="() => handleShowAssetItem(asset, index)"
    @delete-asset="
    handleRemoveAssetItem(index)
    "
  />
  </ul>
</template>

<script setup lang="ts">
import type { AssetDataTypeWithoutS3Object } from '../types';
import AssetCard from '@/components/tokens/aws_infra/plan_generator/AssetCard.vue';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';

const props = defineProps<{
  assetType: AssetTypesEnum;
  assetData: AssetDataTypeWithoutS3Object[] | null;
}>();

const emit = defineEmits(['show-asset-details', 'delete-asset']);

function handleShowAssetItem(asset: AssetDataTypeWithoutS3Object, index: number) {
  emit('show-asset-details', asset, index);
}

function handleRemoveAssetItem(
  index: number
) {
  emit('delete-asset', index);
}
</script>

<style lang="scss" scoped>

</style>
