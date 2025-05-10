import { ref } from 'vue';
import { generateDataChoice } from '@/api/awsInfra';
import { getTokenData } from '@/utils/dataService';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';

export function useGenerateAssetName(
  assetType: AssetTypesEnum,
  fieldType: string
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

  async function handleGenerateName() {
    try {
      const res = await generateDataChoice(
        tokenId.value,
        authId.value,
        assetType,
        fieldType
      );
      if (!res.data.result) {
        isGenerateNameError.value = res.data.message;
      }
      generatedName.value = res.data.proposed_data;
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
