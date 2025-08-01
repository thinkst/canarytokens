import { ref } from 'vue';
import { generateDataChoice } from '@/api/awsInfra';
import { generateDataChoice as generateDataChoiceTest } from '@/views/planPreviewUtils.ts';
import { getTokenData } from '@/utils/dataService';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';

export function useGenerateAssetName(
  assetType: AssetTypesEnum,
  fieldType: string,
  updateAiAvailableNames: (count: number) => void
) {
  const isGenerateNameError = ref('');
  const isGenerateNameLoading = ref(false);
  const generatedName = ref('');
  const authId = ref('');
  const tokenId = ref('');

  const tokenData = getTokenData();

  if (tokenData) {
    const { auth_token, token } = tokenData;
    authId.value = auth_token;
    tokenId.value = token;
  }

  isGenerateNameLoading.value = true;
  isGenerateNameError.value = '';

  const isPreviewMode = window.location.pathname.includes('/nest/plan-preview');

  async function handleGenerateName() {
    if (isPreviewMode) {
      const res = await generateDataChoiceTest();
      //@ts-ignore
      generatedName.value = res.proposed_data;
      isGenerateNameLoading.value = false;
      return;
    }
    try {
      const res = await generateDataChoice(
        tokenId.value,
        authId.value,
        assetType,
        fieldType
      );

      if (res.status === 429) {
        isGenerateNameError.value =
          'You have reached your limit for AI-generated decoy names. You can continue with manual setup.';
        return;
      }

      if (!res.data.result) {
        isGenerateNameError.value = res.data.message;
      }

      generatedName.value = res.data.proposed_data;
      const availableAiNamesCount = res.data.data_generation_remaining || 0;
      updateAiAvailableNames(availableAiNamesCount);
    } catch (err: any) {
      isGenerateNameError.value = err.message || 'An error occurred';
    } finally {
      isGenerateNameLoading.value = false;
    }
  }
  return {
    handleGenerateName,
    isGenerateNameError,
    isGenerateNameLoading,
    generatedName,
  };
}
