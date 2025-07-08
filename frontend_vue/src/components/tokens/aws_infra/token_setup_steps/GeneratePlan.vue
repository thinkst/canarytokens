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
import { savePlan } from '@/api/awsInfra.ts';
import type { TokenDataType } from '@/utils/dataService';
import type {
  ProposedAWSInfraTokenPlanData,
  AssetData,
} from '@/components/tokens/aws_infra/types.ts';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';
import AssetCategoryCard from '../plan_generator/AssetCategoryCard.vue';
import ModalAsset from '@/components/tokens/aws_infra/plan_generator/ModalAsset.vue';

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

const isErrorMessage = ref('');
const isSavingPlan = ref(false);
const isSaveError = ref(false);
const isSaveErrorMessage = ref('');
const isSaveSuccess = ref(false);
const isLoadingUI = ref(true);

const assetSamples = ref<ProposedAWSInfraTokenPlanData>({
  S3Bucket: [],
  SQSQueue: [],
  SSMParameter: [],
  SecretsManagerSecret: [],
  DynamoDBTable: [],
});

onMounted(() => {
  assetSamples.value = proposed_plan.assets as ProposedAWSInfraTokenPlanData;
  // Set loading state to allow UI to render
  setTimeout(() => {
    isLoadingUI.value = false;
  }, 300);
});

const availableAssets = computed(() => {
  return Object.values(AssetTypesEnum).reduce(
    (acc, assetType) => {
      const assetData = assetSamples.value[assetType];
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
  console.log('handleSaveAsset save asset!!!')
  if (!assetSamples.value[assetType]) {
    assetSamples.value[assetType] = [];
  }
  if (index === -1) {
    (assetSamples.value[assetType] as AssetData[])?.unshift(newValues);
  } else {
    assetSamples.value[assetType]![index] = newValues;
  }
}

async function handleSavePlan(formValues: { assets: AssetData[] | null; }) {
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

async function handleSubmit(formValues: { assets: AssetData[] | null; }) {
  await handleSavePlan(formValues);
}
</script>

<style></style>
