<template>
  <div class="flex flex-row justify-between my-16">
    <div class="flex flex-row gap-8 items-center">
      <img
        :src="iconURL()"
        :alt="`icon ${getLabel(props.assetKey)}`"
        class="h-[2rem] w-[2rem]"
      />
      <legend class="flex flex-col">
        <span class="text-grey-500">{{ getLabel(props.assetKey) }}</span>
        <span>{{ getLabel(props.objectKey) }}</span>
      </legend>
    </div>
    <BaseButton
      type="button"
      variant="text"
      icon="plus"
      @click="prepend(ASSET_DATA[objectKey])"
    >
      Add object
    </BaseButton>
  </div>
  <div
    v-for="(field, fieldIndex) in paginatedFields"
    :key="fieldIndex"
    class="ml-32"
  >
    <fieldset
      v-for="(_propertyValue, propertyKey) in field.value"
      :key="propertyKey"
    >
      <AssetTextField
        :id="`${props.assetKey}.${fieldIndex}.${propertyKey}`"
        v-model="field.value[propertyKey]"
        :label="getLabel(propertyKey)"
        variant="small"
        icon="aws_infra_icons/objects.svg"
        :hide-label="true"
        :has-remove="true"
        @handle-remove-instance="remove(fieldIndex)"
      />
    </fieldset>
  </div>
  <div>
    <div class="mt-4">
      <button
        type="button"
        :disabled="currentPageNumber === 1"
        @click.stop="handlePreviousPage"
      >
        Prev
      </button>
      <span class="mx-2">{{ currentPageNumber }} / {{ totalPagesNumber }}</span>
      <button
        type="button"
        :disabled="currentPageNumber === totalPagesNumber"
        @click.stop="handleNextPage"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue';
import {
  ASSET_LABEL,
  ASSET_DATA,
} from '@/components/tokens/aws_infra/constants.ts';
import getImageUrl from '@/utils/getImageUrl';
import AssetTextField from '@/components/tokens/aws_infra/plan_generator/AssetTextField.vue';

const props = defineProps<{
  assetKey: keyof typeof ASSET_LABEL;
  objectKey: keyof typeof ASSET_DATA;
  fields: any;
  prepend: (value: any) => void;
  remove: (value: number) => void;
}>();

const MAX_PER_PAGE = 5;
const currentPageNumber = ref(1);

const paginatedFields = computed(() => {
  const startIndex = (currentPageNumber.value - 1) * MAX_PER_PAGE;
  const endIndex = currentPageNumber.value * MAX_PER_PAGE;
  return props.fields.slice(startIndex, endIndex);
});
const totalPagesNumber = computed(() => {
  return Math.ceil(props.fields.length / MAX_PER_PAGE);
});

function iconURL() {
  return getImageUrl(`aws_infra_icons/${props.assetKey}.svg`);
}

function getLabel(key: keyof typeof ASSET_LABEL) {
  return ASSET_LABEL[key];
}

function handlePreviousPage() {
  if (currentPageNumber.value >= 1) {
    currentPageNumber.value--;
  }
}

function handleNextPage() {
  if (currentPageNumber.value < totalPagesNumber.value) {
    currentPageNumber.value++;
  }
}
</script>
