<template>
  <BaseModal
    :title="`Delete ${props.assetType}`"
    :has-close-button="true"
  >
    Are you sure you want to delete this {{ assetType }}?
    <template #footer>
      <div class="flex flex-16 gap-16">
        <BaseButton
          variant="secondary"
          @click="props.closeModal"
          >No, keep it</BaseButton
        >
        <BaseButton
          variant="danger"
          @click="handleDeleteAsset"
          >Delete</BaseButton
        >
      </div>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ASSET_TYPE } from '@/components/tokens/aws_infra/constants.ts';

type AssetConstKeyType = keyof typeof ASSET_TYPE;
type AssetConstValuesType = (typeof ASSET_TYPE)[AssetConstKeyType];

const props = defineProps<{
  assetType: AssetConstValuesType;
  closeModal: () => void;
  onDeleteConfirmed: () => void;
}>();

function handleDeleteAsset() {
  props.closeModal();
  props.onDeleteConfirmed();
}
</script>
