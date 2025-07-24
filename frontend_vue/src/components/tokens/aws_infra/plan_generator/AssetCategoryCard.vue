<template>
  <li class="asset_category_card__wrapper">
    <button
      ref="assetCardRef"
      v-tooltip="{
        content: isLoadingData ? 'Loading decoys...' : '',
        triggers: ['hover'],
      }"
      class="asset_category_card group"
      :class="{ loading: isLoadingData }"
      :aria-label="`Open ${assetCategoryName} assets`"
      @click.stop="handleAssetClick"
    >
      <!-- Content -->
      <div class="asset_category_card__content">
        <img
          v-if="!isLoadingData"
          :src="getImageUrl(`aws_infra_icons/${props.assetType}.svg`)"
          :alt="`logo-${assetType}`"
          class="rounded-full w-[5rem] h-[5rem]"
          :class="assetData?.length ? '' : 'grayscale opacity-50'"
        />
        <span v-else>
          <base-skeleton-loader
            class="w-[5rem] h-[5rem] rounded-full"
            :loading="isLoadingData"
          />
        </span>
        <p class="text-grey-600 text-pretty mt-8">
          {{ assetCategoryName }}
        </p>
      </div>
      <ul class="asset_category_card__list-data">
        <li class="text-sm">
          <span class="label text-grey-400">Totaly decoys:</span>
          <span class="value"> {{ totalAssets }}</span>
        </li>
      </ul>
      <!--- Btn Edit --->
      <div class="asset_category_card__btn-edit">
        {{ assetData?.length ? 'Review' : 'Add Decoys' }}
      </div>
    </button>
  </li>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import getImageUrl from '@/utils/getImageUrl';
import type { AssetData } from '../types';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';
import { getAssetLabel } from '@/components/tokens/aws_infra/plan_generator/assetService.ts';

const emit = defineEmits(['openAsset', 'deleteAsset', 'selectAsset']);

const props = defineProps<{
  assetType: AssetTypesEnum;
  assetData: AssetData[];
  isLoadingData: boolean;
}>();

const assetCardRef = ref();
const isLoadingData = computed(() => props.isLoadingData);

const assetCategoryName = computed(() => {
  return getAssetLabel(props.assetType);
});

const totalAssets = computed(() => {
  if (!props.assetData) {
    return 0;
  }
  return Object.keys(props.assetData).length;
});

function handleAssetClick() {
  if (isLoadingData.value) {
    return;
  }
  emit('openAsset');
}
</script>

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
    border: 1px solid;
    background-color: white;
    transition-duration: 100ms;
    transition-timing-function: ease-in-out;
    @apply border-grey-300 rounded-2xl gap-8;

    &.loading {
      opacity: 0.7;
    }

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
      height: 2rem;
      padding-block: 0.5rem;
      align-items: center;
      line-height: 0.8rem;
      border-top: 2px solid;
      height: 2rem;
      border-bottom-left-radius: 1rem;
      border-bottom-right-radius: 1rem;
      transition: all 100ms linear;
      @apply border-grey-50 text-grey-700 shadow-solid-shadow-grey  font-semibold;
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

<style>
.asset_category_card.active:not(.loading),
.asset_category_card:hover:not(.loading),
.asset_category_card:focus:not(.loading),
.asset_category_card:focus-within:not(.loading) {
  @apply border-green-600 shadow-solid-shadow-green-600-sm;

  .asset_category_card__btn-edit {
    @apply text-white border-b-green-600 shadow-solid-shadow-green-600-sm bg-green-500 outline-none;
  }
}
</style>
