<template>
  <div class="infra-token__title-wrapper">
    <h2>Design your Decoys</h2>
  </div>
  <div
    v-if="isLoadingUI"
    class="mt-[80px] grid gap-8 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 auto-rows-fr"
  >
    <BaseSkeletonLoader
      v-for="i in 10"
      :key="i"
      type="rectangle"
      class="h-[160px]"
    />
  </div>
  <div
    v-if="!isLoadingUI"
    class="flex items-stretch flex-col px-24"
  >
    <div>
      <div class="flex justify-between mb-24">
        <!-- <div>
          <SelectAddAsset
            :is-type-missing-permission="isMissingPermissionAssetType"
            @select-option="(assetKey) => handleAddNewAsset(assetKey)"
          />
        </div> -->
        <!-- <div class="flex items-center gap-8 text-grey-500">
          View:
          <button
            type="button"
            :class="{ 'text-green-500': viewType === ViewTypeEnum.LIST }"
            @click="handleSelectViewType(ViewTypeEnum.LIST)"
          >
            List
          </button>
          |
          <button
            type="button"
            :class="{ 'text-green-500': viewType === ViewTypeEnum.GRID }"
            @click="handleSelectViewType(ViewTypeEnum.GRID)"
          >
            Grid
          </button>
        </div> -->
      </div>
      <div class="min-h-[3rem] flex items-center">
        <!-- Filters -->
        <!-- <div
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
        </div> -->
        <!-- Bulk select actions -->
        <!-- <div
          v-if="numberSelectedAssets"
          class="bg-grey-100 rounded-xl px-24 py-8 flex flex-row w-fit gap-8"
        >
          <span>{{ numberSelectedAssets }} assets selected: </span>
          <button
            type="button"
            class="font-semibold hover:text-red"
            @click="handleRemoveAsset(null, null, 0, true)"
          >
            Delete Selected
          </button>
          <button
            type="button"
            class="ml-8 font-semibold hover:text-green-500"
            @click="resetSelectedAssetObj"
          >
            Unselect All
          </button>
        </div> -->
      </div>
      <BaseMessageBox
        v-if="isErrorMessage"
        variant="danger"
        >{{ isErrorMessage }}</BaseMessageBox
      >
      <ul
        class="grid gap-16 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-5 auto-rows-fr"
      >
        <AssetCategoryCard
          v-for="(_assetValue, assetKey, index) of assetSamples"
          :key="`${assetKey}-${index}`"
          :asset-type="assetKey as AssetTypesEnum"
          :asset-data="assetSamples[assetKey]"
          @open-asset="
            handleOpenAssetCategoryModal(
              assetSamples[assetKey],
              assetKey as AssetTypesEnum
            )
          "
        />
      </ul>
      <!-- <template
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
                  viewType === ViewTypeEnum.LIST,
              },
              {
                'grid gap-8 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 auto-rows-fr':
                  viewType === ViewTypeEnum.GRID,
              },
            ]"
          >
          <TransitionGroup :name="animationName">
              <AssetCard
                v-for="(asset, index) of assetValues"
                :key="`${assetKey}-${Object.values(asset)[0]}`"
                :asset-type="assetKey as AssetTypesEnum"
                :view-type="viewType"
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
              :asset-type="assetKey as AssetTypesEnum"
              @add-asset="handleAddNewAsset(assetKey as AssetTypesEnum)"
            />
          </div>
        </section>
      </template> -->
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
import { ref, onMounted, computed } from 'vue';
import { useModal } from 'vue-final-modal';
import { savePlan } from '@/api/awsInfra.ts';
import type { TokenDataType } from '@/utils/dataService';
import type {
  AssetsTypes,
  AssetDataType,
} from '@/components/tokens/aws_infra/types.ts';
import type { PlanValueTypes } from '@/components/tokens/aws_infra/types.ts';
// import { useGenerateAssetName } from '@/components/tokens/aws_infra/plan_generator/useGenerateAssetName.ts';
// import FilterButton from '@/components/ui/FilterButton.vue';
// import AssetCard from '@/components/tokens/aws_infra/plan_generator/AssetCard.vue';
import {
  // ASSET_LABEL,
  // ASSET_DATA,
  AssetTypesEnum,
} from '@/components/tokens/aws_infra/constants.ts';

// import ModalDelete from '@/components/tokens/aws_infra/plan_generator/ModalDeleteAsset.vue';
// import ButtonAddAsset from '@/components/tokens/aws_infra/plan_generator/ButtonAddAsset.vue';
// import SelectAddAsset from '@/components/tokens/aws_infra/plan_generator/SelectAddAsset.vue';
// import useMultiselectAssets from '@/components/tokens/aws_infra/plan_generator/useMultiselectAssets.ts';
import AssetCategoryCard from '../plan_generator/AssetCategoryCard.vue';
import ModalAsset from '@/components/tokens/aws_infra/plan_generator/ModalAsset.vue';

// enum ViewTypeEnum {
//   GRID = 'gridView',
//   LIST = 'listView',
// }

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  initialStepData: TokenDataType;
}>();

const token = '123445abc';
const auth_token = '123445abc';
// const code_snippet_command = '';
const proposed_plan = {
  assets: {
    S3Bucket: [
      {
        bucket_name: 'prod-audit-bucket-viuopht59s',
        objects: [
          {
            object_path: '2010/UMpE4oF15s/data',
          },
          {
            object_path: '2018/gEw6cLtq05/passwords',
          },
          {
            object_path: '2006/xe4Wmu34p3/object',
          },
          {
            object_path: '2012/X2WFYabC6o/data',
          },
          {
            object_path: '2022/zB6XCodOWc/text',
          },
          {
            object_path: '2012/HAqOZwAxOh/data',
          },
          {
            object_path: '2022/u1kAo2Ii3e/text',
          },
          {
            object_path: '2013/CXh519HXVP/passwords',
          },
          {
            object_path: '2013/GgD8jYtqR5/passwords',
          },
          {
            object_path: '2011/AOwMC23YSN/passwords',
          },
          {
            object_path: '2004/CLc9Yt40HA/text',
          },
          {
            object_path: '2019/qru7hnsb0H/passwords',
          },
          {
            object_path: '2021/CuJpjsRabs/passwords',
          },
          {
            object_path: '2020/a0hzyns7WV/passwords',
          },
          {
            object_path: '2001/PWhdTKK294/data',
          },
          {
            object_path: '2006/dt1vJ7BIB9/passwords',
          },
          {
            object_path: '2013/Fww1gEHoFB/data',
          },
          {
            object_path: '2001/sfBO3jJLjC/data',
          },
          {
            object_path: '2015/WYlsYi9d80/passwords',
          },
          {
            object_path: '2019/2DmepxdzJN/data',
          },
          {
            object_path: '2010/ufX3mOLX8S/data',
          },
          {
            object_path: '2001/JrNG74NI4J/data',
          },
          {
            object_path: '2004/TeKv9zerxz/text',
          },
          {
            object_path: '2020/10XmEtszzY/passwords',
          },
          {
            object_path: '2005/b7MP9pdqng/passwords',
          },
          {
            object_path: '2016/7srPnGKiKq/object',
          },
          {
            object_path: '2011/cgvFlEee5d/object',
          },
          {
            object_path: '2023/KUx8cQACbl/passwords',
          },
          {
            object_path: '2012/5xutyqsVhu/passwords',
          },
          {
            object_path: '2006/3MfLA5Yz6D/object',
          },
          {
            object_path: '2008/GKlyFIsSS9/passwords',
          },
          {
            object_path: '2019/UVwjEFR4lo/object',
          },
          {
            object_path: '2025/y8lN43zaOO/text',
          },
          {
            object_path: '2001/8Rw5soCdUL/object',
          },
          {
            object_path: '2009/phoCpenYEw/object',
          },
          {
            object_path: '2023/Puf32VPvNB/text',
          },
          {
            object_path: '2022/3N63vxHI7J/text',
          },
          {
            object_path: '2002/a7IENvKBvb/object',
          },
          {
            object_path: '2005/Ipx9VJ9uMZ/passwords',
          },
          {
            object_path: '2021/XWPHTJZgNO/data',
          },
          {
            object_path: '2002/OU04pIo9gh/text',
          },
          {
            object_path: '2018/wvOYP5xmTs/data',
          },
          {
            object_path: '2009/D7AlttyZ0J/passwords',
          },
          {
            object_path: '2001/yRHsKcDTbl/passwords',
          },
          {
            object_path: '2023/d4mRYlmQbg/text',
          },
          {
            object_path: '2001/3zfMvg2yHM/data',
          },
          {
            object_path: '2004/4yldeXK81G/object',
          },
          {
            object_path: '2005/p2D6X3Akbq/object',
          },
          {
            object_path: '2024/YSzGqNbzoV/passwords',
          },
          {
            object_path: '2024/fpuEcXlsPW/text',
          },
          {
            object_path: '2018/54BBRZrGkA/text',
          },
          {
            object_path: '2003/DZ7HfGUygd/text',
          },
          {
            object_path: '2019/jIhT4g7rGf/text',
          },
          {
            object_path: '2013/Lw8RXt7WXC/text',
          },
          {
            object_path: '2020/miuLxExBhz/object',
          },
          {
            object_path: '2006/ZsWcmujE8C/data',
          },
          {
            object_path: '2000/x3gi1XJIBU/passwords',
          },
          {
            object_path: '2006/p3uqaSKeWo/text',
          },
          {
            object_path: '2010/B6Sb2AmHu2/data',
          },
          {
            object_path: '2022/tl0Mp8BFn5/passwords',
          },
          {
            object_path: '2021/BOvDkdjd9Y/passwords',
          },
        ],
        off_inventory: false,
      },
      {
        bucket_name: 'prod-audit-bucket-tkks92yc7d',
        objects: [],
        off_inventory: false,
      },
      {
        bucket_name: 'stagingcustomerbucketoqjw7gucz4',
        objects: [],
        off_inventory: false,
      },
    ],
    SSMParameter: [
      {
        ssm_parameter_name: 'WWOgKCpwUQN',
        ssm_parameter_value: 'qu4KO9eybT5uW',
        off_inventory: false,
      },
      {
        ssm_parameter_name: '2qXEHM',
        ssm_parameter_value: 'fds91LIiMlwg7v',
        off_inventory: false,
      },
    ],
    SecretsManagerSecret: [
      {
        secretsmanager_secret_name: '0HrXF',
        secretsmanager_secret_value: 'kUZypC10r',
        off_inventory: false,
      },
      {
        secretsmanager_secret_name: '3dcr5XkRFNpvySfVr',
        secretsmanager_secret_value: 'jK9hW0U2FE40zTHZM',
        off_inventory: false,
      },
    ],
    DynamoDBTable: [
      {
        dynamodb_name: '0F5Gsi',
        dynamodb_partition_key: 'JuqvGiGkPnXexlrgOu',
        dynamodb_row_count: '8',
        off_inventory: false,
      },
    ],
    SQSQueue: [
      {
        queue_name: 'XDAXOfW',
        message_count: '1',
        off_inventory: false,
      },
    ],
  },
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
// const { token, auth_token, code_snippet_command, proposed_plan } =
//   props.initialStepData;

// const viewType = ref(ViewTypeEnum.GRID);
const isLoading = ref(true);
const isErrorMessage = ref('');
const isSavingPlan = ref(false);
const isSaveError = ref(false);
const isSaveErrorMessage = ref('');
const isSaveSuccess = ref(false);
const isLoadingUI = ref(true);

const assetSamples = ref<AssetsTypes>({
  S3Bucket: [],
  SQSQueue: [],
  SSMParameter: [],
  SecretsManagerSecret: [],
  DynamoDBTable: [],
});

// const filterValue = ref('');
// const {
//   isActiveSelected,
//   numberSelectedAssets,
//   handleRemoveAllSelected,
//   handleSelectAsset,
//   resetSelectedAssetObj,
// } = useMultiselectAssets(assetSamples);

onMounted(() => {
  assetSamples.value = proposed_plan.assets;
  // resetSelectedAssetObj();

  // Set loading state to allow UI to render
  setTimeout(() => {
    isLoadingUI.value = false;
  }, 300);
});

const isMissingPermissionAssetType = computed(() => {
  return Object.entries(assetSamples.value)
    .filter(([, v]) => v === null)
    .map(([k]) => k);
});

// function handleRemoveManageInfo(assetData: any) {
//   // eslint-disable-next-line @typescript-eslint/no-unused-vars
//   const { off_inventory, ...rest } = assetData;
//   return rest;
// }

// function handleSelectViewType(value: ViewTypeEnum) {
//   viewType.value = value;
// }

// function handleFilterList(assetType: AssetTypesEnum) {
//   filterValue.value = assetType;
// }

// function showSection(assetType: AssetTypesEnum) {
//   return filterValue.value === assetType || filterValue.value === '';
// }

// function handleRemoveAsset(
//   assetType: any,
//   list: any,
//   index: number,
//   isBulkDelete: boolean
// ) {
//   const { open, close } = useModal({
//     component: ModalDelete,
//     attrs: {
//       assetType: assetType,
//       isBulkDelete: isBulkDelete,
//       closeModal: () => {
//         close();
//       },
//       onDeleteConfirmed: () => {
//         !isBulkDelete ? list.splice(index, 1) : handleRemoveAllSelected();
//       },
//     },
//   });
//   open();
// }

function handleDeleteAsset(assetType: AssetTypesEnum, index: number) {
  console.log('handleDeleteAsset', assetType, index);
  assetSamples.value[assetType]!.splice(index, 1);
}

function handleOpenAssetCategoryModal(
  assetData: AssetDataType,
  assetType: AssetTypesEnum
) {
  const { open, close } = useModal({
    component: ModalAsset,
    attrs: {
      assetType: assetType,
      assetData: assetData,
      closeModal: () => {
        close();
      },
      'onUpdate-asset': (newValues) => {
        console.log('onUpdate-asset', newValues);
        const { assetType, assetData, index } = newValues;
        handleSaveAsset(assetType, assetData, index);
      },
      'onDelete-asset': (index: number) => {
        handleDeleteAsset(assetType, index);
      },
      'onAdd-asset': (newValues) => {
        handleSaveAsset(assetType, newValues, -1);
      },
    },
  });
  open();
}

// async function handleAddNewAsset(assetType: AssetTypesEnum) {
//   const newAssetFields = () => {
//     switch (assetType) {
//       case AssetTypesEnum.S3BUCKET:
//         return ASSET_DATA[AssetTypesEnum.S3BUCKET];
//       case AssetTypesEnum.SQSQUEUE:
//         return ASSET_DATA[AssetTypesEnum.SQSQUEUE];
//       case AssetTypesEnum.SSMPARAMETER:
//         return ASSET_DATA[AssetTypesEnum.SSMPARAMETER];
//       case AssetTypesEnum.SECRETMANAGERSECRET:
//         return ASSET_DATA[AssetTypesEnum.SECRETMANAGERSECRET];
//       case AssetTypesEnum.DYNAMODBTABLE:
//         return ASSET_DATA[AssetTypesEnum.DYNAMODBTABLE];
//       default:
//         return {};
//     }
//   };

//   const newAssetValues: Record<string, any> = { ...newAssetFields() };

//   async function getAssetRandomData() {
//     isLoading.value = true;

//     try {
//       const results = await Promise.all(
//         Object.keys(newAssetFields()).map(async (key) => {
//           if (Array.isArray(newAssetValues[key])) return null;
//           if (key === 'off_inventory') return { key, value: false };

//           const {
//             handleGenerateName,
//             isGenerateNameError,
//             isGenerateNameLoading,
//             generatedName,
//           } = useGenerateAssetName(assetType, key);

//           isLoading.value = isGenerateNameLoading.value;
//           await handleGenerateName();
//           isErrorMessage.value = isGenerateNameError.value;
//           return { key, value: generatedName.value };
//         })
//       );

//       results.forEach((result) => {
//         if (result) {
//           newAssetValues[result.key] = result.value;
//         }
//       });
//     } catch (err: any) {
//       isErrorMessage.value = err.message || 'An error occurred';
//     } finally {
//       isLoading.value = false;
//     }
//   }

//   await getAssetRandomData();
//   handleSaveAsset(newAssetValues, assetType, -1);
//   // scroll to section
//   location.href = `#section-${assetType}`;
// }

function handleSaveAsset(
  assetType: AssetTypesEnum,
  newValues: any,
  index: number
) {
  console.log('handleSaveAsset save asset!!!')
  if (!assetSamples.value[assetType]) {
    assetSamples.value[assetType] = [];
  }
  if (index === -1) {

    assetSamples.value[assetType].unshift(newValues);
  } else {
    assetSamples.value[assetType]![index] = newValues;
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

.loading-enter-active,
.loading-leave-active {
  transition: all 0.4s ease;
  transition-delay: 0.2s;
}
.loading-enter-from,
.loading-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}

.loading-enter-active {
  animation-delay: 0.8s;
}
</style>
