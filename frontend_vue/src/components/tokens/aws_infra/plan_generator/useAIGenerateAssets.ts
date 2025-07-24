import {
  hasAiGeneratedField,
  getAssetNameKey,
} from '@/components/tokens/aws_infra/plan_generator/assetService';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';
import type { ProposedAWSInfraTokenPlanData } from '@/components/tokens/aws_infra/types.ts';

type FormattedDataForAI = {
  assets: {
    [key in keyof AssetTypesEnum]: string[];
  };
};

export function useAIGenerateAssets() {
  function formatDataForAIRequest(
    initialAssetData: ProposedAWSInfraTokenPlanData
  ): FormattedDataForAI {
    const aiEnabledAssets = Object.fromEntries(
      Object.entries(initialAssetData)
        .filter(([assetType]) => {
          const aiCompatibleFields = hasAiGeneratedField(
            assetType as AssetTypesEnum
          );
          return aiCompatibleFields.length > 0;
        })
        .map(([assetType, assetList]) => {
          const nameField = getAssetNameKey(assetType as AssetTypesEnum);
          const assetNames = assetList.map((fields) => fields[nameField]);
          return [assetType, assetNames];
        })
    );

    return { assets: aiEnabledAssets };
  }

  function mergeAIGeneratedAssets(
    existingAssetsData: ProposedAWSInfraTokenPlanData,
    generatedAssets: Record<string, Record<string, string[]>>
  ): ProposedAWSInfraTokenPlanData {
    const mergedAssets = Object.entries(generatedAssets).reduce(
      (acc, current) => {
        const assetType = current[0];
        const generatedAssetsForType = current[1];

        const fieldToPopulate = hasAiGeneratedField(assetType).toString();
        const assetNameKey = getAssetNameKey(assetType);

        const currentAssets = existingAssetsData[assetType] || [];
        const updatedAssets = [...currentAssets];

        Object.entries(generatedAssetsForType).forEach(
          ([assetName, fieldValues]) => {
            const existingAsset = updatedAssets.find(
              (asset) => asset[assetNameKey] === assetName
            );

            if (!existingAsset) return;

            const existingAssetIndex = updatedAssets.indexOf(existingAsset);
            updatedAssets[existingAssetIndex] = {
              ...updatedAssets[existingAssetIndex],
              [fieldToPopulate]: fieldValues,
            };
          }
        );

        return {
          ...acc,
          [assetType]: updatedAssets,
        };
      },
      {}
    );

    return { ...existingAssetsData, ...mergedAssets };
  }

  return {
    formatDataForAIRequest,
    mergeAIGeneratedAssets,
  };
}
