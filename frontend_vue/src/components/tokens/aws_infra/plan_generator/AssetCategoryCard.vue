<template>
  <li class="asset_category_card__wrapper">
    <button
      ref="assetCardRef"
      class="asset_category_card group border group bg-white rounded-2xl top-[0px] border-grey-200 duration-100 ease-in-out"
      @click.stop="handleAssetClick"
      @mouseover="handleMouseOver"
      @focus="handleMouseOver"
      @mouseleave="handleMouseLeave"
      @blur="handleMouseLeave"
    >
      <!-- Content -->
      <div class="asset_category_card__content">
        <img
          :src="getImageUrl(`aws_infra_icons/${props.assetType}.svg`)"
          :alt="`logo-${assetType}`"
          class="rounded-full w-[5rem] h-[5rem]"
          :class="assetData ? '' : 'grayscale opacity-50'"
        />
        <p class="text-grey-600 text-pretty mt-8">
          {{ assetCategoryName }}
        </p>
      </div>
      <ul class="asset_category_card__list-data list-none">
        <li class="text-sm">
          <span class="label text-grey-400">Totaly decoys:</span>
          <span class="value"> {{ totalAssets }}</span>
        </li>
      </ul>
      <!--- Btn Edit --->
      <div
        class="asset_category_card__btn-edit text-sm w-full leading-5 font-semibold border-t-2 border-grey-50 text-grey-700 h-[2rem] rounded-b-2xl transition duration-100 shadow-solid-shadow-grey"
      >
        {{ assetData ? 'Review' : 'Add Decoys' }}
      </div>
    </button>
  </li>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import getImageUrl from '@/utils/getImageUrl';
import type { AssetDataTypeWithoutS3Object } from '../types';
import {
  ASSET_DATA_NAME,
  ASSET_LABEL,
  AssetTypesEnum,
} from '@/components/tokens/aws_infra/constants.ts';

const emit = defineEmits(['openAsset', 'deleteAsset', 'selectAsset']);

const props = defineProps<{
  assetType: AssetTypesEnum;
  assetData: any | AssetDataTypeWithoutS3Object | null;
}>();

const isHoverCard = ref(false);
const assetCardRef = ref();

const assetCategoryName = computed(() => {
  return ASSET_LABEL[props.assetType as keyof typeof ASSET_DATA_NAME];
});

const totalAssets = computed(() => {
  if (!props.assetData) {
    return 0;
  }
  return Object.keys(props.assetData).length;
});

function handleAssetClick() {
  // Open Modal
  emit('openAsset');
  // remove focus from selected card
  if (assetCardRef.value) {
    assetCardRef.value.blur();
  }
}

function handleMouseOver() {
  isHoverCard.value = true;
}

function handleMouseLeave() {
  isHoverCard.value = false;
}
</script>

<style>
.asset_category_card.active,
.asset_category_card:hover,
.asset_category_card:focus,
.asset_category_card:focus-within {
  @apply border-green-600 shadow-solid-shadow-green-600-sm;

  .asset_category_card__btn-edit {
    @apply text-white border-b-green-600 shadow-solid-shadow-green-600-sm bg-green-500 outline-none;
  }
}
</style>

<style lang="scss" scoped>
.asset_category_card__wrapper {
  position: relative;
  display: flex;
  align-items: stretch;

  .asset_category_card {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    justify-content: space-between;
    align-items: stretch;
    gap: 0.5rem;

    &__content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8;
      padding-inline: 0.5rem;
      padding-top: 0.8rem;

      p {
        padding-block: 0.3rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 20ch;
      }
    }

    &__list-data {
      padding-bottom: 0.5rem;
      padding-inline: 0.5rem;

      li {
        display: flex;
        flex-direction: row;
        gap: 0.5rem;
        justify-content: space-between;
        text-align: left;

        span.value {
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          max-width: 10ch;
        }
      }
    }
    &__btn-edit {
      padding-block: 0.5rem;
      align-items: center;
      line-height: 0.8rem;
    }

    &__options {
      display: none;
      align-items: center;

      .list-btn-edit {
        display: none;
      }

      .input-select {
        position: absolute;
        left: 0.8rem;
        top: 0.7rem;
      }

      .list-btn-edit {
        position: absolute;
        right: 3em;
        top: 0.6rem;
      }

      .btn-delete {
        position: absolute;
        right: 0.5rem;
        top: 0.5rem;
      }
    }
  }

  &:hover,
  &:focus,
  &:active,
  &:focus-within {
    .asset-card__options {
      display: flex;
    }
  }
}
</style>
