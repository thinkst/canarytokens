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
import type { ComputedRef } from 'vue';
import type { AssetData } from '../types';
import AssetCard from '@/components/tokens/aws_infra/plan_generator/AssetCard.vue';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';

const props = defineProps<{
  assetType: AssetTypesEnum;
  // The Modal struggles to track reactive data, so this prop is unusual:
  // assetData is a ComputedRef to ensure reactivity
  // AssetType[] is used to ensure type safety in the template
  assetData: AssetData[] | ComputedRef<AssetData[] | null>;
}>();

const emit = defineEmits(['show-asset-details', 'delete-asset']);

function handleShowAssetItem(asset: AssetData, index: number) {
  emit('show-asset-details', asset, index);
}

function handleRemoveAssetItem(
  index: number
) {
  emit('delete-asset', index);
}

</script>
