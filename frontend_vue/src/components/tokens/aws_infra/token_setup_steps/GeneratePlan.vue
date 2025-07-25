<template>
  <div class="infra-token__title-wrapper">
    <h2>Design your Decoys</h2>
  </div>
  <div
    v-if="isLoadingUI"
    class="mt-[20px] grid gap-16 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-5 auto-rows-fr"
  >
    <BaseSkeletonLoader
      v-for="i in 5"
      :key="i"
      type="rectangle"
      class="h-[210px]"
    />
  </div>
  <div
    v-if="!isLoadingUI"
    class="flex items-stretch flex-col px-24"
  >
    <BaseMessageBox
      v-if="isAiGenerateErrorMessage"
      variant="warning"
      class="mt-16"
      text-link="Try again"
      @click="handleRetryAIAssets"
    >
      {{ isAiGenerateErrorMessage }}
    </BaseMessageBox>
    <div>
      <div class="flex justify-between mb-24"></div>
      <BaseMessageBox
        v-if="isErrorMessage"
        variant="danger"
        >{{ isErrorMessage }}</BaseMessageBox
      >
      <ul
        class="grid gap-16 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-5 auto-rows-fr"
      >
        <AssetCategoryCard
          v-for="(assetValues, assetKey, index) in availableAssets"
          :key="`${assetKey}-${index}`"
          :asset-data="assetValues"
          :asset-type="assetKey as AssetTypesEnum"
          :is-loading-data="getIsLoadingAssetData(assetKey as AssetTypesEnum)"
          @open-asset="handleOpenAssetCategoryModal(assetKey as AssetTypesEnum)"
        />
      </ul>
      <BaseMessageBox
        v-if="assetsWithMissingPermissions.length > 0"
        variant="warning"
        class="mt-16"
      >
        {{ assetWithMissingPermissionText }}
      </BaseMessageBox>
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
import { savePlan, requestAIgeneratedAssets } from '@/api/awsInfra.ts';
import type { TokenDataType } from '@/utils/dataService';
import type { TokenSetupData } from '@/components/tokens/aws_infra/types.ts';
import type {
  ProposedAWSInfraTokenPlanData,
  AssetData,
} from '@/components/tokens/aws_infra/types.ts';
import {
  formatDataForAIRequest,
  mergeAIGeneratedAssets,
} from '../plan_generator/AIGenerateAssetsUtils';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';
import AssetCategoryCard from '../plan_generator/AssetCategoryCard.vue';
import ModalAsset from '@/components/tokens/aws_infra/plan_generator/ModalAsset.vue';

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  initialStepData: TokenDataType;
  currentStepData: TokenSetupData;
}>();

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const { token, auth_token, code_snippet_command, proposed_plan } =
  props.initialStepData;

const isErrorMessage = ref('');
const isSavingPlan = ref(false);
const isSaveError = ref(false);
const isSaveErrorMessage = ref('');
const isSaveSuccess = ref(false);
const isLoadingUI = ref(true);
const isLoadingAssetCard = ref<Record<AssetTypesEnum, boolean>>({
  S3Bucket: false,
  SQSQueue: false,
  SSMParameter: false,
  SecretsManagerSecret: false,
  DynamoDBTable: false,
});
const isAiGenerateErrorMessage = ref('');

const assetsData = ref<ProposedAWSInfraTokenPlanData>({
  S3Bucket: [],
  SQSQueue: [],
  SSMParameter: [],
  SecretsManagerSecret: [],
  DynamoDBTable: [],
});

onMounted(() => {
  const isExistingPlan = props.currentStepData?.proposed_plan;

  if (isExistingPlan) {
    assetsData.value = props.currentStepData
      .proposed_plan as ProposedAWSInfraTokenPlanData;
    isLoadingUI.value = false;
    return;
  }

  assetsData.value = proposed_plan.assets as ProposedAWSInfraTokenPlanData;
  fetchAIgeneratedAssets(assetsData.value);
  // Set loading state to allow UI to render
  setTimeout(() => {
    isLoadingUI.value = false;
  }, 300);
});

const availableAssets = computed(() => {
  return Object.values(AssetTypesEnum).reduce(
    (acc, assetType) => {
      const assetData = assetsData.value[assetType];
      if (assetData === null) {
        return acc;
      }
      acc[assetType] = assetData || [];
      return acc;
    },
    {} as Record<AssetTypesEnum, AssetData[]>
  );
});

const assetsWithMissingPermissions = computed(() => {
  return Object.entries(assetsData.value)
    .filter(([, assets]) => assets === null)
    .map(([assetType]) => assetType);
});

const assetWithMissingPermissionText = computed(() => {
  const isMultipleAssets = assetsWithMissingPermissions.value.length > 1;
  return `We couldn't inventory the following asset${isMultipleAssets ? 's' : ''}:
  ${assetsWithMissingPermissions.value.join(', ')}.
  Please check the permissions and run the inventory again.`;
});

function getIsLoadingAssetData(assetType: AssetTypesEnum): boolean {
  return isLoadingAssetCard.value[assetType] || false;
}

function handleDeleteAsset(assetType: AssetTypesEnum, index: number) {
  assetsData.value[assetType]!.splice(index, 1);
}

function handleOpenAssetCategoryModal(assetType: AssetTypesEnum) {
  const { open, close } = useModal({
    component: ModalAsset,
    attrs: {
      assetType: assetType,
      assetData: computed(() => availableAssets.value[assetType]),
      closeModal: () => {
        close();
      },
      'onUpdate-asset': (newValues) => {
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

const resetAssetCardsLoadingState = () => {
  Object.keys(isLoadingAssetCard.value).forEach((assetType) => {
    isLoadingAssetCard.value[assetType as AssetTypesEnum] = false;
  });
};

function handleRetryAIAssets() {
  isAiGenerateErrorMessage.value = '';
  fetchAIgeneratedAssets(assetsData.value);
}

async function fetchAIgeneratedAssets(
  initialAssetData: ProposedAWSInfraTokenPlanData
) {
  const payload = formatDataForAIRequest(initialAssetData);
  let updatedPlanData = {};

  // Update AI generation loading state
  isAiGenerateErrorMessage.value = '';
  Object.keys(payload.assets).forEach((assetType) => {
    isLoadingAssetCard.value[assetType as AssetTypesEnum] = true;
  });

  try {
    const res = await requestAIgeneratedAssets({
      canarytoken: token,
      auth_token: auth_token,
      assets: payload.assets,
    });

    if (res.status === 429) {
      isAiGenerateErrorMessage.value =
        'You have reached your daily limit for AI-generated decoy names. You can continue with manual setup or try again later.';
      resetAssetCardsLoadingState();
      return;
    }

    if (res.status !== 200) {
      isAiGenerateErrorMessage.value =
        res.data?.message ||
        'We encountered an issue while generating AI assets. You can continue setting up your decoys manually or try again.';
      resetAssetCardsLoadingState();
      return;
    }
    const newAssets = res.data.assets;

    if (Object.keys(newAssets).length > 0) {
      updatedPlanData = mergeAIGeneratedAssets(assetsData.value, newAssets);
    }

    assetsData.value = { ...assetsData.value, ...updatedPlanData };
    resetAssetCardsLoadingState();
  } catch (err: any) {
    isAiGenerateErrorMessage.value =
      err.data?.message ||
      'We encountered an issue while generating AI assets. You can continue setting up your decoys manually or try again.';
    resetAssetCardsLoadingState();
  }
}

function handleSaveAsset(
  assetType: AssetTypesEnum,
  newValues: AssetData,
  index: number
) {
  if (!assetsData.value[assetType]) {
    assetsData.value[assetType] = [];
  }
  if (index === -1) {
    (assetsData.value[assetType] as AssetData[])?.unshift(newValues);
  } else {
    assetsData.value[assetType]![index] = newValues;
  }
}

async function handleSavePlan(formValues: { assets: AssetData[] | null }) {
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
      return;
    }
    isSaveSuccess.value = true;
    emits('storeCurrentStepData', {
      token,
      auth_token,
      proposed_plan: assetsData.value,
    });
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

async function handleSubmit(formValues: { assets: AssetData[] | null }) {
  await handleSavePlan(formValues);
}
</script>

<style></style>
