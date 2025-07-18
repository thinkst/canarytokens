<template>
  <li class="asset-card__wrapper">
    <span
      v-if="isOffInventory"
      v-tooltip="{
        html: true,
        content:
          'We couldn`t find this resource in your inventory.<br/>If you wish to remove it permanently, delete it from the list.',
      }"
      class="asset-card__badge text-xs text-white bg-yellow rounded-lg px-4 py-[2px] absolute"
      >Not found</span
    >
    <button
      ref="assetCardRef"
      class="asset-card group border group bg-white rounded-2xl top-[0px] border-grey-200 duration-100 ease-in-out"
      :class="{
        'border-yellow': isOffInventory,
      }"
      @click.stop="handleAssetClick"
      @mouseover="handleMouseOver"
      @focus="handleMouseOver"
      @mouseleave="handleMouseLeave"
      @blur="handleMouseLeave"
    >
      <!-- Content -->
      <div class="asset-card__content">
        <img
          :src="getImageUrl(`aws_infra_icons/${props.assetType}.svg`)"
          :alt="`logo-${assetType}`"
          class="rounded-full"
        />
        <p class="text-sm text-grey-400 text-pretty">
          {{ assetName }}
        </p>
      </div>
      <ul class="asset-card__list-data list-none">
        <li
          v-for="[key, value] in assetCardProperties"
          :key="key"
          class="text-sm"
        >
          <span class="label text-grey-400"> {{ ASSET_LABEL[key] }}: </span>
          <span
            class="value text-grey-700"
            :class="{ 'with-icon': ASSET_WITH_ICON.includes(key) }"
          >
            <img
              v-if="ASSET_WITH_ICON.includes(key)"
              :src="getImageUrl(`aws_infra_icons/${key}.svg`)"
              :alt="`${key} icon`"
              class="w-[1.5rem] h-[1.5rem]"
            />
            <span :class="{ 'cropped-data': assetCardProperties.length > 1 }">
              {{ value }}</span
            ></span
          >
        </li>
      </ul>
    </button>
    <div class="asset-card__options">
      <button
        type="button"
        class="list-btn-edit text-sm text-grey-400"
        @click.stop="handleAssetClick"
      >
        Edit
      </button>
      <button
        v-tooltip="{
          content: 'Delete asset',
        }"
        type="button"
        class="btn-delete w-[1.5rem] text-grey-300 rounded-full hover:text-green-500"
        aria-label="Delete asset"
        @click="emit('deleteAsset')"
      >
        <font-awesome-icon
          aria-hidden="true"
          icon="trash"
        ></font-awesome-icon>
      </button>
    </div>
  </li>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import getImageUrl from '@/utils/getImageUrl';
import {
  ASSET_DATA_NAME,
  ASSET_LABEL,
  ASSET_WITH_ICON,
  AssetTypesEnum,
} from '@/components/tokens/aws_infra/constants.ts';
import type { AssetData } from '../types';

const emit = defineEmits(['showAsset', 'deleteAsset', 'selectAsset']);

const props = defineProps<{
  assetType: AssetTypesEnum;
  assetData: AssetData;
}>();

const isHoverCard = ref(false);
const assetCardRef = ref();

const assetName = computed(() => {
  const nameKey = ASSET_DATA_NAME[props.assetType];
  return props.assetData[nameKey as keyof AssetData];
});

const assetCardProperties = computed(() => {
  const nameKey = ASSET_DATA_NAME[props.assetType];

  const assets = Object.entries(props.assetData)
    .map(([key, value]) => {
      if (key.includes(nameKey)) return null;
      // For Edit mode
      if (key.includes('off_inventory')) return null;
      if (Array.isArray(value)) return [key, value.length];
      return [key, value];
    })
    .filter((asset) => asset !== null);
  return assets as [keyof AssetData, string | number][];
});

const isOffInventory = computed(() => {
  return props.assetData.off_inventory;
});


function handleAssetClick() {
  emit('showAsset');
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
.asset-card.active,
.asset-card:hover,
.asset-card:focus,
.asset-card:focus-within {
  @apply border-green-600 shadow-solid-shadow-green-600-sm;

  .asset-card__btn-edit {
    @apply text-white border-b-green-600 shadow-solid-shadow-green-600-sm bg-green-500 outline-none;
  }
}
</style>

<style lang="scss">
.asset-card__wrapper {
  display: flex;
  position: relative;
  container-type: inline-size;

  .asset-card {
    display: flex;
    flex-grow: 1;
    gap: 0.5rem;
    padding-block: 0.8rem;
    padding-inline: 0.5rem;

    &__badge {
      top: -6px;
      right: 0.4rem;
    }

    &__content {
      display: flex;
      flex-direction: row;
      gap: 0.5rem;
      flex-shrink: 0;
      align-items: center;
      padding-left: 2rem;

      p {
        width: 30ch;
        text-align: left;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        padding-right: 1rem;

        @media (max-width: 1024px) {
          width: auto;
        }

        @media (max-width: 768px) {
          width: 20ch;
        }
      }

      img {
        height: 1.5rem;
        width: 1.5rem;
        border-radius: 2rem;
      }
    }

    &__list-data {
      display: flex;
      flex-direction: row;
      flex-wrap: wrap;
      padding-right: 5rem;
      padding-left: 1rem;

      @media (max-width: 768px) {
        flex-direction: column;
        align-items: start;
      }

      li {
        padding-inline: 1rem;
        text-align: left;
        display: flex;
        flex-direction: row;
        gap: 0.5rem;
        line-height: 1.5rem;

        .cropped-data {
          width: 15ch;
          text-align: left;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        span.value {
          gap: 0.3rem;
          display: flex;
          flex-direction: row;
        }
      }
    }

    &__options {
      align-items: center;

      .input-select {
        position: absolute;
        left: 0.8rem;
        top: 1rem;
      }

      .list-btn-edit {
        position: absolute;
        right: 3em;
        top: 1rem;
      }

      .btn-delete {
        position: absolute;
        right: 0.5rem;
        top: 0.8rem;
      }
    }
  }

  @container (width < 50em) {
    .asset-card:has(.asset-card__list-data li:nth-child(n + 2)) {
      flex-direction: column;
    }
  }

  @container (width < 40em) {
    .asset-card {
      flex-direction: column;
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

  &:hover,
  &:active {
    .list-btn-edit {
      @apply text-green-500;
    }
  }
}

.asset-card.active + .asset-card__options {
  display: flex;
}
</style>
