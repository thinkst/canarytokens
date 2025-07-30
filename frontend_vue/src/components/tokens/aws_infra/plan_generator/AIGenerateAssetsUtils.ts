import {
  hasAiGeneratedField,
  getAssetNameKey,
} from '@/components/tokens/aws_infra/plan_generator/assetService';
import type { AssetData } from '@/components/tokens/aws_infra/types.ts';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';
import type { ProposedAWSInfraTokenPlanData } from '@/components/tokens/aws_infra/types.ts';

type FormattedDataForAI = {
  assets: {
    [key in keyof AssetData]: string[];
  };
};

export function formatDataForAIRequest(
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
        if (!assetList) return [assetType, []];
        const nameField = getAssetNameKey(assetType as AssetTypesEnum);
        const assetNames = assetList.map((fields) => {
          const value = fields[nameField as keyof typeof fields];
          return String(value) || '';
        });
        return [assetType, assetNames];
      })
  );

  return { assets: aiEnabledAssets };
}

export function mergeAIGeneratedAssets(
  currentAssetsData: ProposedAWSInfraTokenPlanData,
  generatedAssets: Record<string, Record<string, string[]>>
): ProposedAWSInfraTokenPlanData {
  const updatedAssets = Object.fromEntries(
    Object.entries(generatedAssets).map(
      ([assetTypeStr, generatedAssetsForType]) => {
        const assetType = assetTypeStr as AssetTypesEnum;

        const fieldToPopulate = hasAiGeneratedField(assetType);
        const assetNameKey = getAssetNameKey(assetType);
        const currentAssets = currentAssetsData[assetType] || [];

        const updatedCurrentAssets = currentAssets.map((asset) => {
          const assetName = String(
            (asset as AssetData)[assetNameKey as keyof AssetData]
          );
          const fieldValues = generatedAssetsForType[assetName];

          return fieldValues
            ? { ...asset, [fieldToPopulate]: fieldValues }
            : asset;
        });

        return [assetType, updatedCurrentAssets];
      }
    )
  );

  return { ...currentAssetsData, ...updatedAssets };
}
