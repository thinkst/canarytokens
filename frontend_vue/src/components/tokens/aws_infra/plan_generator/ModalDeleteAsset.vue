<template>
  <BaseModal
    :title="`Delete ${props.assetType ? props.assetType : ''}`"
    :has-close-button="true"
  >
    Are you sure you want to delete
    <span v-if="assetType">this {{ assetType }}?</span>
    <span v-if="isBulkDelete">all selected assets?</span>
    <template #footer>
      <div class="flex flex-16 gap-16">
        <BaseButton
          variant="secondary"
          @click="props.closeModal"
          >No, keep <span v-if="assetType">it</span>
          <span v-if="isBulkDelete">them</span></BaseButton
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
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';

const props = defineProps<{
  assetType: AssetTypesEnum;
  isBulkDelete: boolean;
  closeModal: () => void;
  onDeleteConfirmed: () => void;
}>();

function handleDeleteAsset() {
  props.closeModal();
  props.onDeleteConfirmed();
}
</script>
