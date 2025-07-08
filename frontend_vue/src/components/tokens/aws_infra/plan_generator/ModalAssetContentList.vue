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
    handleRemoveAssetItem(index as number)
    "
  />
  </ul>
</template>

<script setup lang="ts">
// import { ref, computed, onMounted } from 'vue';
import type { AssetDataType } from '../types';
import AssetCard from '@/components/tokens/aws_infra/plan_generator/AssetCard.vue';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';

const props = defineProps<{
  assetType: AssetTypesEnum;
  assetData: AssetDataType;
}>();

const emit = defineEmits(['show-asset-details', 'delete-asset']);

function handleShowAssetItem(asset: AssetDataType, index: number) {
  // Emit an event to open the asset modal
  console.log('handleShowAssetItem', asset, index);
  emit('show-asset-details', asset, index);
}

function handleRemoveAssetItem(
  index: number
) {
  // Emit an event to delete the asset
  emit('delete-asset', index);
}
</script>

<style lang="scss" scoped>

</style>
