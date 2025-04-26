import { ref, computed } from 'vue';
import type { Ref } from 'vue';
import type { AssetsTypes } from '@/components/tokens/aws_infra/types';

export default function useMultiselectAsset(assetsData: Ref<AssetsTypes>) {
  const selectedAssets: Ref<any[]> = ref([]);
  const isActiveSelected = ref(false);

  const numberSelectedAssets = computed(() => {
    let selectedItems = 0;

    selectedAssets.value.forEach((obj) => {
      const indexArray = Object.values(obj)[0];

      if (Array.isArray(indexArray)) {
        selectedItems += indexArray.length;
      }
    });

    return selectedItems;
  });

  function resetSelectedAssetObj() {
    isActiveSelected.value = false;
    selectedAssets.value = Object.keys(assetsData.value).map((key) => {
      return { [key]: [] };
    });
  }

  function handleSelectAsset(
    isSelected: boolean,
    assetKey: string,
    index: number
  ) {
    const assetObject = selectedAssets.value.find((item) => assetKey in item);

    if (isSelected) {
      isActiveSelected.value = true;
      if (
        assetObject &&
        Array.isArray(assetObject[assetKey]) &&
        !assetObject[assetKey].includes(index)
      ) {
        assetObject[assetKey].push(index);
      }
    }

    if (!isSelected) {
      if (assetObject && Array.isArray(assetObject[assetKey])) {
        assetObject[assetKey] = assetObject[assetKey].filter(
          (item) => item !== index
        );
      }
    }
  }

  function handleRemoveAllSelected() {
    const updatedAssets = { ...assetsData.value };

    selectedAssets.value.forEach((assetGroup) => {
      const assetKey = Object.keys(assetGroup)[0];
      const indicesToRemove = assetGroup[assetKey];
      // Order indexes in descending order
      // To avoid weird shifting in index order during the loop
      const sortedIndicesToRemove = [...indicesToRemove].sort((a, b) => b - a);

      if (
        updatedAssets[assetKey as keyof typeof assetsData.value] &&
        Array.isArray(indicesToRemove)
      ) {
        sortedIndicesToRemove.forEach((index) => {
          if (index >= 0 && index < updatedAssets[assetKey].length) {
            updatedAssets[assetKey].splice(index, 1);
          }
        });
      }
    });

    assetsData.value = updatedAssets;
    resetSelectedAssetObj();
  }

  return {
    isActiveSelected,
    numberSelectedAssets,
    handleRemoveAllSelected,
    handleSelectAsset,
    resetSelectedAssetObj,
  };
}
