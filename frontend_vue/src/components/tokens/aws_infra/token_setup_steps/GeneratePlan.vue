<template>
  <div class="infra-token__title-wrapper">
    <div class="grid md:grid-cols-3 gap-16 justify-center items-center">
      <span></span>
      <h2>Review your Decoys</h2>
      <div
        class="flex flex-row items-center md:justify-end gap-16 justify-center"
      >
        <p>Name generation requests left</p>
        <BaseSkeletonLoader
          v-if="getAnyLoadingAssetData()"
          class="w-[2.5rem] h-[2.5rem] shrink-0"
          type="circle"
        />
        <div
          v-else
          v-tooltip="{
            content: aiCurrentAvailableNamesCountTootlip,
            triggers: ['hover'],
          }"
          class="ai-name-count"
          :style="styleAiNameCountProgressBar"
          role="progressbar"
          :aria-valuemax="totalAiQuota"
          aria-valuemin="0"
          :aria-valuenow="availableAiQuota"
        >
          <span>{{ availableAiQuota }} </span>
        </div>
      </div>
    </div>
  </div>
  <BaseSkeletonLoader
    v-if="getAnyLoadingAssetData() || isLoadingUI"
    class="mb-24"
    type="rectangle"
    style="height: 100px; width: 100%"
  />
  <div
    v-if="isLoadingUI"
    class="mt-[20px] grid gap-16 grid-cols-1 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-5 auto-rows-fr"
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
      class="mt-16 mb-16"
    >
      {{ isAiGenerateErrorMessage }}
    </BaseMessageBox>
    <div>
      <div v-if="!getAnyLoadingAssetData() && !isAiGenerateErrorMessage">
        <BaseMessageBox
          :variant="getPlanIntroMessageVariant"
          class="mb-24"
        >
          {{ getPlanIntroMessage }}
        </BaseMessageBox>
      </div>
      <ul
        class="grid gap-16 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 auto-rows-fr"
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
        class="mt-16 mb-16"
      >
        {{ assetWithMissingPermissionText }}
      </BaseMessageBox>
    </div>

    <div class="flex flex-col items-center mt-32">
      <BaseButton
        :loading="isSavingPlan"
        :disabled="getAnyLoadingAssetData()"
        @click="handleSavePlan()"
        >{{ isSavingPlan ? 'Saving...' : 'Save configuration' }}</BaseButton
      >
      <BaseMessageBox
        v-if="isSaveError"
        class="mt-24"
        variant="danger"
        >{{ isSaveErrorMessage }}</BaseMessageBox
      >
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useModal } from 'vue-final-modal';
import { savePlan } from '@/api/awsInfra.ts';
import type { TokenDataType } from '@/utils/dataService';
import type { TokenSetupData } from '@/components/tokens/aws_infra/types.ts';
import type {
  ProposedAWSInfraTokenPlanData,
  AssetData,
} from '@/components/tokens/aws_infra/types.ts';
import { useAIGeneratedAssets } from '@/components/tokens/aws_infra/plan_generator/useAIGenerateAssets.ts';

import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';
import AssetCategoryCard from '@/components/tokens/aws_infra/plan_generator/AssetCategoryCard.vue';
import ModalAsset from '@/components/tokens/aws_infra/plan_generator/ModalAsset.vue';
import { setTempAssetsData } from '@/components/tokens/aws_infra/plan_generator/planTempService.ts';
import {
  getAIQuotaState,
  setTotalAIQuota,
  setAvailableAIQuota,
  INITIAL_AI_QUOTA,
} from '@/components/tokens/aws_infra/plan_generator/AIQuotaService.ts';

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  initialStepData: TokenDataType;
  currentStepData: TokenSetupData;
}>();

const {
  token,
  auth_token,
  proposed_plan,
  available_ai_names,
  is_managing_token,
} = props.initialStepData;

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
const { totalAiQuota, availableAiQuota } = getAIQuotaState();

const assetsData = ref<ProposedAWSInfraTokenPlanData>({
  S3Bucket: [],
  SQSQueue: [],
  SSMParameter: [],
  SecretsManagerSecret: [],
  DynamoDBTable: [],
});

const resetAssetCardsLoadingState = () => {
  Object.keys(isLoadingAssetCard.value).forEach((assetType) => {
    isLoadingAssetCard.value[assetType as AssetTypesEnum] = false;
  });
};

const {
  isAiGenerateErrorMessage,
  fetchAIgeneratedAssets,
  aiGeneratedAssetsCount,
} = useAIGeneratedAssets(
  token,
  auth_token,
  assetsData,
  updateAiCurrentAvailableNamesCount,
  resetAssetCardsLoadingState,
  isLoadingAssetCard
);

onMounted(() => {
  const isExistingSession = props.currentStepData?.proposed_plan;

  if (isExistingSession) {
    assetsData.value = props.currentStepData
      .proposed_plan as ProposedAWSInfraTokenPlanData;
    isLoadingUI.value = false;
    return;
  }

  if (proposed_plan.assets && Object.keys(proposed_plan.assets).length > 0) {
    assetsData.value = proposed_plan.assets as ProposedAWSInfraTokenPlanData;
  } else {
    assetsData.value = {
      S3Bucket: [],
      SQSQueue: [],
      SSMParameter: [],
      SecretsManagerSecret: [],
      DynamoDBTable: [],
    };
  }

  if (!is_managing_token) fetchAIgeneratedAssets(assetsData.value);
  else updateAiCurrentAvailableNamesCount(available_ai_names);

  // Set loading state to allow UI to render
  setTimeout(() => {
    isLoadingUI.value = false;
  }, 300);
});

const styleAiNameCountProgressBar = computed(() => {
  const total = totalAiQuota.value;
  const available = availableAiQuota.value;
  const progress = total ? Math.min((available / total) * 100, 100) : 0;

  if (available > 20) return `--bar-color: #22c55e; --progress: ${progress}%;`;
  if (available > 8) return `--bar-color: #eab308; --progress: ${progress}%;`;
  return `--bar-color: #ef4444; --progress: ${progress}%;`;
});

const aiCurrentAvailableNamesCountTootlip = computed(() => {
  return availableAiQuota.value > 0
    ? `We generate decoy names with AI. You have ${availableAiQuota.value} names available out of ${totalAiQuota.value}.`
    : 'You have reached your limit for generated names. You can continue with manual setup.';
});

const getPlanIntroMessageVariant = computed(() => {
  if (
    totalAiQuota.value <= 0 &&
    availableAiQuota.value <= 0 &&
    !is_managing_token
  ) {
    return 'warning';
  }
  return 'success';
});

const getPlanIntroMessage = computed(() => {
  if (
    totalAiQuota.value <= 0 &&
    availableAiQuota.value <= 0 &&
    !is_managing_token
  ) {
    return "We analyzed your AWS account. It's not possible to generate decoys for your AWS account because you've run out of credits. However, you can still manually set up the decoys and then generate your Canarytoken.";
  }

  if (is_managing_token) {
    return 'We analysed your account. You can review or edit the decoy resources before we generate your Terraform module.';
  }

  return `We analysed your account. Based on the names (and quantities) of your existing resources, we suggest adding the following ${aiGeneratedAssetsCount.value} decoy resources into your account. You can review or edit this before we generate your Terraform module.`;
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

function getAnyLoadingAssetData(): boolean {
  return Object.values(isLoadingAssetCard.value).some((loading) => loading);
}

function updateAiCurrentAvailableNamesCount(count: number) {
  if (is_managing_token) setTotalAIQuota(INITIAL_AI_QUOTA);
  if (totalAiQuota.value === 0) setTotalAIQuota(Math.floor(count) || 0);
  setAvailableAIQuota(Math.floor(count) || 0);
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

async function handleSavePlan() {
  isSavingPlan.value = true;
  isSaveError.value = false;
  isSaveErrorMessage.value = '';
  isSaveSuccess.value = false;

  const planValues = {
    assets: assetsData.value,
  };

  try {
    const res = await savePlan(token, auth_token, planValues);
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
      is_managing_token,
    });
    emits('updateStep');
  } catch (err: any) {
    isSaveError.value = true;
    isSaveErrorMessage.value =
      err.response?.data?.message ||
      err.message ||
      'We couldn`t save the plan. Please, try again';
    isSaveSuccess.value = false;
  } finally {
    isSavingPlan.value = false;
  }
}

watch(
  assetsData,
  (newAssets) => {
    setTempAssetsData(newAssets);
  },
  { deep: true }
);
</script>

<style>
.ai-name-count {
  --bar-color: #22c55e;
  --progress: 0%;
  font-weight: bold;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;

  background-image: conic-gradient(
    var(--bar-color) var(--progress),
    hsl(156, 9%, 89%) 0%
  );

  span {
    position: absolute;
    color: var(--bar-color);
  }

  &::after {
    content: '';
    width: 2rem;
    height: 2rem;
    border-radius: 1rem;
    background-color: white;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>
