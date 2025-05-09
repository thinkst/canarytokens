<template>
  <div class="flex mb-24 items-center gap-24">
    <p>Choose the sample type of data to populate the Plan:</p>
    <BaseButton
      variant="text"
      icon="arrow-right"
      @click.stop="handleChangePlanSampleData('regular')"
      >Show Regular plan (default)</BaseButton
    >
    <BaseButton
      variant="text"
      icon="arrow-right"
      @click.stop="handleChangePlanSampleData('missingPermission')"
      >Show Missing SQS Queue permission plan</BaseButton
    >
    <BaseButton
      variant="text"
      icon="arrow-right"
      @click.stop="handleChangePlanSampleData('manage')"
      >Show Manage Token plan</BaseButton
    >
  </div>
  <div class="p-40 bg-grey-50 rounded-xl">
    <div class="flex justify-between mb-24">
      <div>
        <SelectAddAsset
          :is-type-missing-permission="isMissingPermissionAssetType"
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
    <div class="min-h-[3rem] flex items-center">
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
    <BaseMessageBox
      v-if="isErrorMessage"
      variant="danger"
      >{{ isErrorMessage }}</BaseMessageBox
    >

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
        <div v-if="isMissingPermissionAssetType.includes(assetKey)">
          <BaseMessageBox variant="warning"
            >We couldn't inventory your {{ ASSET_LABEL[assetKey] }}. Please
            check the permissions and run the inventory again.</BaseMessageBox
          >
        </div>
        <div
          v-else
          :class="[
            {
              'grid grid-col-1 gap-8 auto-rows-fr': viewType === VIEW_TYPE.LIST,
            },
            {
              'grid gap-8 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 auto-rows-fr':
                viewType === VIEW_TYPE.GRID,
            },
          ]"
        >
          <TransitionGroup :name="animationName">
            <AssetCard
              v-for="(asset, index) of assetValues"
              :key="`${assetKey}-${Object.values(asset)[0]}`"
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
import { ref, provide, onMounted, computed } from 'vue';
import type { Ref } from 'vue';
import { useModal } from 'vue-final-modal';
import { generateDataChoice } from '@/api/awsInfra.ts';
import type {
  AssetsTypes,
  AssetDataType,
} from '@/components/tokens/aws_infra/types.ts';
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

// Start handle Samples plan
import {
  assetsExample,
  assetsWithEmptySQSQueue,
  assetsManageExample,
} from './planPreviewUtils.ts';

function handleChangePlanSampleData(type: string) {
  if (type === 'regular') {
    assetSamples.value = assetsExample.value;
  }
  if (type === 'missingPermission') {
    assetSamples.value = assetsWithEmptySQSQueue.value;
  }
  if (type === 'manage') {
    assetSamples.value = assetsManageExample.value;
  }
}
// End handle Sample plan

type ViewTypeValue = (typeof VIEW_TYPE)[keyof typeof VIEW_TYPE];
type AssetConstKeyType = keyof typeof ASSET_TYPE;
type AssetConstValuesType = (typeof ASSET_TYPE)[AssetConstKeyType];

const VIEW_TYPE = {
  GRID: 'gridView',
  LIST: 'listView',
} as const;

const assetSamples = ref<AssetsTypes>({
  [ASSET_TYPE.S3BUCKET]: null,
  [ASSET_TYPE.SQSQUEUE]: null,
  [ASSET_TYPE.SSMPARAMETER]: null,
  [ASSET_TYPE.SECRETMANAGERSECRET]: null,
  [ASSET_TYPE.DYNAMODBTABLE]: null,
});

const viewType: Ref<ViewTypeValue> = ref(VIEW_TYPE.GRID);
const isLoading = ref(false);
const isErrorMessage = ref('');
const filterValue = ref('');
const animationName = ref('list');
const {
  isActiveSelected,
  numberSelectedAssets,
  handleRemoveAllSelected,
  handleSelectAsset,
  resetSelectedAssetObj,
} = useMultiselectAssets(assetSamples);

provide('viewType', viewType);

onMounted(() => {
  assetSamples.value = assetsWithEmptySQSQueue.value;
  resetSelectedAssetObj();
});

const isMissingPermissionAssetType = computed(() => {
  return Object.entries(assetSamples.value)
    .filter(([, v]) => v === null)
    .map(([k]) => k);
});

function handleRemoveManageInfo(assetData: any) {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { offInventory, ...rest } = assetData;
  return rest;
}

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

function handleOpenAssetModal(
  assetData: AssetDataType,
  assetType: AssetConstValuesType,
  index: number
) {
  const { open, close } = useModal({
    component: ModalAsset,
    attrs: {
      assetType: assetType,
      assetData: handleRemoveManageInfo(assetData),
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

  const newAssetValues: Record<string, any> = { ...newAssetFields() };

  async function getAssetRandomData() {
    isLoading.value = true;

    try {
      const results = await Promise.all(
        Object.keys(newAssetFields()).map(async (key) => {
          if (Array.isArray(newAssetValues[key])) return null;

          const res = await generateDataChoice(assetType);
          if (!res.result) {
            isErrorMessage.value = res.message;
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
}

function handleSaveAsset(
  newValues: any,
  assetType: AssetConstValuesType,
  index: number
) {
  if (!assetSamples.value[assetType]) {
    assetSamples.value[assetType] = [];
  }
  if (index === -1) {
    assetSamples.value[assetType]!.push(newValues);
  } else {
    animationName.value = '';
    assetSamples.value[assetType][index] = newValues;
    setTimeout(() => {
      animationName.value = 'list';
    }, 0);
  }
}

function handleSavePlan() {
  alert(JSON.stringify(assetSamples.value));
}
</script>

<style>
@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  20% {
    transform: translateY(-10px);
  }
  40% {
    transform: translateY(10px);
  }
  60% {
    transform: translateY(-5px);
  }
  80% {
    transform: translateY(5px);
  }
}

.list-enter-active,
.list-leave-active {
  transition: all 0.4s ease;
  transition-delay: 0.2s;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}

.list-enter-active {
  animation: bounce 1.2s ease infinite;
  animation-delay: 0.8s;
}
</style>
