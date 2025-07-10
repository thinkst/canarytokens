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
      :loading="isLoading"
      @click="handleAddObject"
    >
      Add object
    </BaseButton>
  </div>
  <BaseMessageBox
    v-if="isErrorMessage"
    variant="danger"
    >{{ isErrorMessage }}
  </BaseMessageBox>
  <div class="paginated_object_list__wrapper">
    <fieldset
      class="paginated_object_list"
      :style="{
        '--page-count': totalPagesNumber,
        '--list-rows': totalPagesNumber > 1 ? MAX_PER_PAGE : fields.length,
        '--scroll-position': `${scrollPosition}`,
        '--container-width': `${containerWidth}px`,
      }"
    >
      <div
        v-for="(field, fieldIndex) in fields"
        :key="fieldIndex"
        class="object_item pl-24"
      >
        <div
          v-for="(_propertyValue, propertyKey) in field.value"
          :key="propertyKey"
        >
          <AssetTextField
            :id="`${props.assetKey}.${fieldIndex}.${propertyKey}`"
            :value="field.value[propertyKey]"
            :label="getLabel(propertyKey as any)"
            :field-type="objectKey"
            variant="small"
            icon="aws_infra_icons/objects.svg"
            :hide-label="true"
            :has-remove="true"
            :asset-type="props.assetType"
            @handle-remove-instance="remove(fieldIndex)"
          />
        </div>
      </div>
    </fieldset>
  </div>
  <div
    v-if="totalPagesNumber > 1"
    class="flex flex-col items-center"
  >
    <div class="mt-16 flex flex-row gap-16">
      <button
        type="button"
        :disabled="currentPageNumber === 1"
        class="text-grey-200 hover:text-green-500 pointer"
        @click.stop="handlePreviousPage"
      >
        <span class="sr-only">Prev</span>
        <font-awesome-icon
          icon="chevron-left"
          aria-hidden="true"
        />
      </button>
      <button
        v-for="page in totalPagesNumber"
        :key="page"
        class="w-[1.5rem] h-[1.5rem] border border-solid border-grey-300 rounded-full text-sm text-grey-400 hover:text-green-500 pointer"
        type="button"
        @click.stop="currentPageNumber = page"
      >
        <span
          :class="{ 'text-grey-700 font-semibold': currentPageNumber === page }"
          >{{ page }}</span
        >
      </button>
      <button
        type="button"
        :disabled="currentPageNumber === totalPagesNumber"
        class="text-grey-200 hover:text-green-500 pointer"
        @click.stop="handleNextPage"
      >
        <span class="sr-only">Next</span>
        <font-awesome-icon
          icon="chevron-right"
          aria-hidden="true"
        />
      </button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue';
import {
  ASSET_LABEL,
  AssetTypesEnum,
} from '@/components/tokens/aws_infra/constants.ts';
import type { AssetDataType, S3ObjectType } from '../types';
import getImageUrl from '@/utils/getImageUrl';
import AssetTextField from '@/components/tokens/aws_infra/plan_generator/AssetTextField.vue';
import { useGenerateAssetName } from '@/components/tokens/aws_infra/plan_generator/useGenerateAssetName.ts';

const props = defineProps<{
  assetType: AssetTypesEnum;
  assetKey: keyof AssetDataType;
  objectKey: keyof S3ObjectType;
  fields: any;
  prepend: (value: any) => void;
  remove: (value: number) => void;
}>();

const MAX_PER_PAGE = 10;
const currentPageNumber = ref(1);
const containerWidth = ref(0);
const isLoading = ref(false);
const isErrorMessage = ref('');

const totalPagesNumber = computed(() => {
  return Math.ceil(props.fields.length / MAX_PER_PAGE);
});

const objectKey = computed(() => props.objectKey);

onMounted(() => {
  checkContainerWidth();
  window.addEventListener('resize', () => checkContainerWidth());
});

const scrollPosition = computed(() => {
  return (currentPageNumber.value - 1) * containerWidth.value;
});

function checkContainerWidth() {
  const element = document.querySelector('.paginated_object_list__wrapper');
  containerWidth.value =
    element instanceof HTMLElement ? element.offsetWidth : 0;
}

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

async function handleAddObject() {
  isLoading.value = true;
  isErrorMessage.value = '';

  const {
    handleGenerateName,
    isGenerateNameError,
    isGenerateNameLoading,
    generatedName,
  } = useGenerateAssetName(props.assetType, props.objectKey);

  isLoading.value = isGenerateNameLoading.value;
  await handleGenerateName();
  isErrorMessage.value = isGenerateNameError.value;
  if (isErrorMessage.value) {
    isLoading.value = false;
    return;
  }
  props.prepend({ [objectKey.value]: generatedName.value });
  isLoading.value = false;
}
</script>

<style lang="scss">
.paginated_object_list__wrapper {
  overflow: hidden;
  opacity: 0;
  animation: fadeIn 0.5s ease-in-out forwards;
}

@keyframes fadeIn {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

.paginated_object_list {
  --page-count: 1;
  --list-rows: 8;
  --container-width: 0px;
  --scroll-position: 0;

  display: grid;
  grid-template-rows: repeat(var(--list-rows), 1fr);
  grid-template-columns: repeat(var(--page-count), var(--container-width));
  grid-auto-flow: column;
  transform: translateX(calc(var(--scroll-position) * -1px));
  transition: 150ms ease-in;
}
</style>
