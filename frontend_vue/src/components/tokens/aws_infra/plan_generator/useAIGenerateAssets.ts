import { ref } from 'vue';
import type { Ref } from 'vue';
import { requestAIgeneratedAssets } from '@/api/awsInfra.ts';
import {
  formatDataForAIRequest,
  mergeAIGeneratedAssets,
} from '@/components/tokens/aws_infra/plan_generator/AIGenerateAssetsUtils';
import type { ProposedAWSInfraTokenPlanData } from '@/components/tokens/aws_infra/types.ts';
import type { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';

export function useAIGeneratedAssets(
  token: string,
  auth_token: string,
  assetsData: Ref<ProposedAWSInfraTokenPlanData>,
  updateAiCurrentAvailableNamesCount: (count: number) => void,
  resetAssetCardsLoadingState: () => void,
  isLoadingAssetCard: Ref<Record<AssetTypesEnum, boolean>>
) {
  const isAiGenerateErrorMessage = ref('');

  async function fetchAIgeneratedAssets(
    initialAssetData: ProposedAWSInfraTokenPlanData
  ) {
    const payload = formatDataForAIRequest(initialAssetData);
    let updatedPlanData = {};

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
          'You have reached your limit for AI-generated decoy names. You can continue with manual setup.';
        return;
      }

      if (res.status !== 200) {
        isAiGenerateErrorMessage.value =
          res.data?.message ||
          'We encountered an issue while generating AI assets. You can continue setting up your decoys manually.';
        return;
      }
      const newAssets = res.data.assets;

      const dataGenerationRemaining = Math.floor(
        res.data.data_generation_remaining
      );
      updateAiCurrentAvailableNamesCount(dataGenerationRemaining);

      if (Object.keys(newAssets).length > 0) {
        updatedPlanData = mergeAIGeneratedAssets(assetsData.value, newAssets);
      }

      assetsData.value = { ...assetsData.value, ...updatedPlanData };
    } catch (err: any) {
      isAiGenerateErrorMessage.value =
        err.data?.message ||
        'We encountered an issue while generating AI assets. You can continue setting up your decoys manually.';
    } finally {
      resetAssetCardsLoadingState();
    }
  }

  return {
    isAiGenerateErrorMessage,
    fetchAIgeneratedAssets,
  };
}
