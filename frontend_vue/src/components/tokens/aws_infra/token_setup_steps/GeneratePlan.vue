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
          @open-asset="
            handleOpenAssetCategoryModal(
              assetKey as AssetTypesEnum
            )
          "
        />
      </ul>
      <BaseMessageBox
        v-if="assetsWithMissingPermissions.length > 0"
        variant="warning"
        class="mt-16">
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
import { savePlan } from '@/api/awsInfra.ts';
import type { TokenDataType } from '@/utils/dataService';
import type {
  AssetDataTypeWithoutS3Object
} from '@/components/tokens/aws_infra/types.ts';
import type { PlanValueTypes } from '@/components/tokens/aws_infra/types.ts';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';
import AssetCategoryCard from '../plan_generator/AssetCategoryCard.vue';
import ModalAsset from '@/components/tokens/aws_infra/plan_generator/ModalAsset.vue';

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  initialStepData: TokenDataType;
}>();


// eslint-disable-next-line @typescript-eslint/no-unused-vars
const { token, auth_token, code_snippet_command, proposed_plan } =
  props.initialStepData;

const isLoading = ref(true);
const isErrorMessage = ref('');
const isSavingPlan = ref(false);
const isSaveError = ref(false);
const isSaveErrorMessage = ref('');
const isSaveSuccess = ref(false);
const isLoadingUI = ref(true);

const assetSamples = ref<Record<AssetTypesEnum, AssetDataTypeWithoutS3Object[] | null>>({
  S3Bucket: [],
  SQSQueue: [],
  SSMParameter: [],
  SecretsManagerSecret: [],
  DynamoDBTable: [],
});

onMounted(() => {
  assetSamples.value = proposed_plan.assets as Record<AssetTypesEnum, AssetDataTypeWithoutS3Object[] | null>;
  // Set loading state to allow UI to render
  setTimeout(() => {
    isLoadingUI.value = false;
  }, 300);
});

const availableAssets = computed(() => {
  return Object.values(AssetTypesEnum).reduce(
    (acc, assetType) => {
      if (
        assetSamples.value[assetType] !== undefined &&
        assetSamples.value[assetType] !== null
      ) {
        acc[assetType] = assetSamples.value[assetType];
      }
      if (assetSamples.value[assetType] === undefined) {
        acc[assetType] = [];
      }
      if (assetSamples.value[assetType] === null) {
        return acc;
      }
      return acc;
    },
    {} as Record<AssetTypesEnum, AssetDataTypeWithoutS3Object[] | [] | null>
  );
});

const assetsWithMissingPermissions = computed(() => {
  return Object.entries(assetSamples.value)
    .filter(([, assets]) => assets === null)
    .map(([assetType]) => assetType);
});


const assetWithMissingPermissionText = computed(() => {
  const isMultipleAssets = assetsWithMissingPermissions.value.length > 1;
  return `We couldn't inventory the following asset${isMultipleAssets ? 's' : ''}:
  ${assetsWithMissingPermissions.value.join(', ')}.
  Please check the permissions and run the inventory again.`;

});

function handleDeleteAsset(assetType: AssetTypesEnum, index: number) {
  assetSamples.value[assetType]!.splice(index, 1);
}

function handleOpenAssetCategoryModal(
  assetType: AssetTypesEnum
) {
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
  newValues: AssetDataTypeWithoutS3Object,
  index: number
) {
  if (!assetSamples.value[assetType]) {
    assetSamples.value[assetType] = [];
  }
  if (index === -1) {
    (assetSamples.value[assetType])?.unshift(newValues);
  } else {
    (assetSamples.value[assetType])![index] = newValues
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

<style></style>
