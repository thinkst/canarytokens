<template>
  <button
    class="border group rounded-2xl top-[0px] border-grey-200 duration-100 ease-in-out hover:border-green-600 focus:border-green-600"
    @click="emits('add-asset')"
  >
    <font-awesome-icon
      aria-hidden="true"
      icon="plus"
      class="group-hover:text-green-600 group-focus:text-green-600 text-grey-300"
    ></font-awesome-icon>
    <span class="sr-only">Add New {{ assetType }}</span>
  </button>
</template>

<script lang="ts" setup>
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';

const emits = defineEmits(['add-asset']);

defineProps<{
  assetType: AssetTypesEnum;
}>();
</script>
