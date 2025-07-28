/* eslint-disable @typescript-eslint/no-unused-vars */
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

// export function mergeAIGeneratedAssets(
//   currentAssetsData: ProposedAWSInfraTokenPlanData,
//   generatedAssets: Record<string, Record<string, string[]>>
// ): ProposedAWSInfraTokenPlanData {
//   const mergedAssets = Object.entries(generatedAssets).reduce(
//     (acc, current) => {
//       const assetType = current[0];
//       const generatedAssetsForType = current[1];

//       const fieldToPopulate = hasAiGeneratedField(
//         assetType as AssetTypesEnum
//       ).toString();
//       const assetNameKey = getAssetNameKey(assetType as AssetTypesEnum);

//       const currentAssets =
//         currentAssetsData[assetType as AssetTypesEnum] || [];
//       const updatedAssets = [...currentAssets];

//       Object.entries(generatedAssetsForType).forEach(
//         ([assetName, fieldValues]) => {
//           console.log(updatedAssets, 'updatedAssets');
//           const existingAsset = updatedAssets.find(
//             (asset) => asset[assetNameKey] === assetName
//           );

//           if (!existingAsset) return;

//           const existingAssetIndex = updatedAssets.indexOf(existingAsset);
//           updatedAssets[existingAssetIndex] = {
//             ...updatedAssets[existingAssetIndex],
//             [fieldToPopulate]: fieldValues,
//           };
//         }
//       );

//       return {
//         ...acc,
//         [assetType]: updatedAssets,
//       };
//     },
//     {}
//   );

//   return { ...currentAssetsData, ...mergedAssets };
// // }

export function mergeAIGeneratedAssets(
  currentAssetsData: ProposedAWSInfraTokenPlanData,
  generatedAssets: Record<string, Record<string, string[]>>
): ProposedAWSInfraTokenPlanData {
  const mergedAssets = Object.entries(generatedAssets).reduce(
    (acc, current) => {
      const assetType = current[0];
      const generatedAssetsForType = current[1];

      const fieldToPopulate = hasAiGeneratedField(
        assetType as AssetTypesEnum
      ).toString();
      const assetNameKey = getAssetNameKey(assetType as AssetTypesEnum);

      const currentAssets =
        currentAssetsData[assetType as AssetTypesEnum] || [];
      const updatedAssets = [...currentAssets];

      Object.entries(generatedAssetsForType).forEach(
        ([assetName, fieldValues]) => {
          const existingAsset = updatedAssets.find((asset) => {
            return (
              String((asset as AssetData)[assetNameKey as keyof AssetData]) ===
              assetName
            );
          });

          if (!existingAsset) return;

          const existingAssetIndex = updatedAssets.indexOf(existingAsset);
          updatedAssets[existingAssetIndex] = {
            ...updatedAssets[existingAssetIndex],
            [fieldToPopulate]: fieldValues,
          };
        }
      );

      console.log(`Updated assets for ${assetType}:`, updatedAssets);

      return {
        ...acc,
        [assetType]: updatedAssets,
      };
    },
    {}
  );

  console.log('Merged assets:', mergedAssets);

  return { ...currentAssetsData, ...mergedAssets };
}
