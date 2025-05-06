import { ref } from 'vue';
import { generateDataChoice } from '@/api/main';

export function useGenerateAssetName(assetType: string) {
  const isGenerateNameError = ref('');
  const isGenerateNameLoading = ref(false);
  const generatedName = ref('');

  isGenerateNameLoading.value = true;
  isGenerateNameError.value = '';

  async function handleGenerateName() {
    try {
      const res = await generateDataChoice(assetType);
      if (!res.result) {
        isGenerateNameError.value = res.message;
      }
      generatedName.value = res.proposed_data;
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
