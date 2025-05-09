<template>
  <div class="infra-token__title-wrapper">
    <h2>Proposed Plan</h2>
  </div>
  <div class="flex items-stretch flex-col px-24">
    <div>
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
                @click="handleFilterList(assetKey as AssetTypesEnum)"
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
          v-if="showSection(assetKey as AssetTypesEnum)"
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
                'grid grid-col-1 gap-8 auto-rows-fr':
                  viewType === VIEW_TYPE.LIST,
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
                :asset-type="assetKey as AssetTypesEnum"
                :asset-data="asset"
                :is-active-selected="isActiveSelected"
                @open-asset="
                  handleOpenAssetModal(asset, assetKey as AssetTypesEnum, index)
                "
                @select-asset="
                  (isSelected) =>
                    handleSelectAsset(
                      isSelected,
                      assetKey as AssetTypesEnum,
                      index
                    )
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
              :asset-type="assetKey"
              @add-asset="handleAddNewAsset(assetKey as AssetTypesEnum)"
            />
          </div>
        </section>
      </template>
    </div>

    <div class="flex flex-col items-center mt-32">
      <BaseButton
        :loading="isSavingPlan"
        @click="handleSubmit(proposed_plan)"
        >{{ isSavingPlan ? 'Saving the plan...' : 'Save Plan' }}</BaseButton
      >
      <BaseMessageBox
        v-if="isSaveError"
        variant="danger"
        >{{ isSaveErrorMessage }}</BaseMessageBox
      >
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, provide, onMounted, computed } from 'vue';
import type { Ref } from 'vue';
import { useModal } from 'vue-final-modal';
import { savePlan } from '@/api/awsInfra.ts';
import type { TokenDataType } from '@/utils/dataService';
import type {
  AssetsTypes,
  AssetDataType,
} from '@/components/tokens/aws_infra/types.ts';
import type { PlanValueTypes } from '@/components/tokens/aws_infra/types.ts';
import StepState from '../StepState.vue';
import { useGenerateAssetName } from '@/components/tokens/aws_infra/plan_generator/useGenerateAssetName.ts';

import FilterButton from '@/components/ui/FilterButton.vue';
import AssetCard from '@/components/tokens/aws_infra/plan_generator/AssetCard.vue';
import {
  ASSET_LABEL,
  ASSET_DATA,
  AssetTypesEnum,
} from '@/components/tokens/aws_infra/constants.ts';
import ModalAsset from '@/components/tokens/aws_infra/plan_generator/ModalAsset.vue';
import ModalDelete from '@/components/tokens/aws_infra/plan_generator/ModalDeleteAsset.vue';
import ButtonAddAsset from '@/components/tokens/aws_infra/plan_generator/ButtonAddAsset.vue';
import SelectAddAsset from '@/components/tokens/aws_infra/plan_generator/SelectAddAsset.vue';
import useMultiselectAssets from '@/components/tokens/aws_infra/plan_generator/useMultiselectAssets.ts';

type ViewTypeValue = (typeof VIEW_TYPE)[keyof typeof VIEW_TYPE];

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  initialStepData: TokenDataType;
}>();

const isLoading = ref(true);
const isError = ref(false);
const isErrorMessage = ref('');
const errorMessage = ref('');
const isSavingPlan = ref(false);
const isSaveError = ref(false);
const isSaveErrorMessage = ref('');
const isSaveSuccess = ref(false);

const assetSamples = ref<AssetsTypes>({
  S3Bucket: [],
  SQSQueue: [],
  SSMParameter: [],
  SecretsManagerSecret: [],
  DynamoDBTable: [],
});

const { token, auth_token, proposed_plan } = props.initialStepData;

const VIEW_TYPE = {
  GRID: 'gridView',
  LIST: 'listView',
} as const;

const viewType: Ref<ViewTypeValue> = ref(VIEW_TYPE.GRID);

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
  assetSamples.value = proposed_plan.assets;
  resetSelectedAssetObj();
});

const isMissingPermissionAssetType = computed(() => {
  return Object.entries(assetSamples.value)
    .filter(([, v]) => v === null)
    .map(([k]) => k);
});

function handleRemoveManageInfo(assetData: any) {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { off_inventory, ...rest } = assetData;
  return rest;
}

function handleSelectViewType(
  value: (typeof VIEW_TYPE)[keyof typeof VIEW_TYPE]
) {
  viewType.value = value;
}

function handleFilterList(assetType: AssetTypesEnum) {
  filterValue.value = assetType;
}

function showSection(assetType: AssetTypesEnum) {
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
  assetType: AssetTypesEnum,
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

async function handleAddNewAsset(assetType: AssetTypesEnum) {
  const newAssetFields = () => {
    switch (assetType) {
      case AssetTypesEnum.S3BUCKET:
        return ASSET_DATA[AssetTypesEnum.S3BUCKET];
      case AssetTypesEnum.SQSQUEUE:
        return ASSET_DATA[AssetTypesEnum.SQSQUEUE];
      case AssetTypesEnum.SSMPARAMETER:
        return ASSET_DATA[AssetTypesEnum.SSMPARAMETER];
      case AssetTypesEnum.SECRETMANAGERSECRET:
        return ASSET_DATA[AssetTypesEnum.SECRETMANAGERSECRET];
      case AssetTypesEnum.DYNAMODBTABLE:
        return ASSET_DATA[AssetTypesEnum.DYNAMODBTABLE];
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
          if (key === 'off_inventory') return { key, value: false };

          const {
            handleGenerateName,
            isGenerateNameError,
            isGenerateNameLoading,
            generatedName,
          } = useGenerateAssetName(assetType, key);

          isLoading.value = isGenerateNameLoading.value;
          await handleGenerateName();
          isErrorMessage.value = isGenerateNameError.value;
          return { key, value: generatedName.value };
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
  assetType: AssetTypesEnum,
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

isLoading.value = false;

async function handleSavePlan(formValues: PlanValueTypes) {
  isSavingPlan.value = true;
  isSaveError.value = false;
  isSaveErrorMessage.value = '';
  isSaveSuccess.value = false;

  try {
    const res = await savePlan(token, auth_token, formValues);
    if (res.status !== 200) {
      isSavingPlan.value = false;
      isSaveError.value = true;
      isSaveErrorMessage.value = res.data.message;
    }
    isSaveSuccess.value = true;
    emits('storeCurrentStepData', { token, auth_token });
    emits('updateStep');
  } catch (err: any) {
    isSaveError.value = true;
    isSaveErrorMessage.value =
      err.message || 'We couldn`t save the plan. Please, try again';
    isSaveSuccess.value = false;
  } finally {
    isSavingPlan.value = false;
  }
}

async function handleSubmit(formValues: PlanValueTypes) {
  await handleSavePlan(formValues);
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
