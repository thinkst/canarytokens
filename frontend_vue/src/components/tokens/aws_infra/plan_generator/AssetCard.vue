<template>
  <li
    class="asset-card__wrapper"
    :class="viewType"
  >
    <button
      ref="assetCardRef"
      class="asset-card group border group bg-white rounded-2xl top-[0px] shadow-solid-shadow-grey border-grey-200 duration-100 ease-in-out"
      :class="{ active: isSelected }"
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
          v-for="[key, value] in assetDataDisplay"
          :key="key"
          class="text-sm"
        >
          <span class="label text-grey-400"> {{ showDataLabel(key) }}: </span>
          <span class="value text-grey-700">
            <img
              v-if="showDataIcon(key)"
              :src="getImageUrl(`aws_infra_icons/${key}.svg`)"
              :alt="`${key} icon`"
              class="w-[1.5rem] h-[1.3rem]"
            />{{ value }}</span
          >
        </li>
      </ul>
      <!--- Btn Edit --->
      <div
        class="asset-card__btn-edit text-sm w-full leading-5 font-semibold border-t-2 border-grey-50 text-grey-700 h-[2rem] rounded-b-2xl transition duration-100 shadow-solid-shadow-grey"
      >
        {{ isHoverCard ? 'Edit' : assetLabel }}
      </div>
    </button>
    <!-- Select and Btn Delete -->
    <div class="asset-card__options">
      <BaseInputCheckbox
        id="select-asset"
        label="Select asset"
        class="input-select text-sm text-grey-500"
        tooltip-content="Select asset"
        :hide-label="true"
        :model-value="isSelected"
        @update:model-value="(value) => handleSelectAsset(value)"
      />
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
import { ref, computed, inject } from 'vue';
import type {
  S3BucketType,
  S3ObjectType,
  SQSQueueType,
  SSMParameterType,
  SecretsManagerSecretType,
  DynamoDBTableType,
} from '../types';
import getImageUrl from '@/utils/getImageUrl';
import {
  ASSET_TYPE,
  ASSET_DATA_NAME,
  ASSET_TYPE_LABEL,
  ASSET_DATA_LABEL,
  ASSET_WITH_ICON,
} from '@/components/tokens/aws_infra/constants.ts';

type AssetConstKeyType = keyof typeof ASSET_TYPE;
type AssetConstValuesType = (typeof ASSET_TYPE)[AssetConstKeyType];
type AssetType =
  | S3BucketType
  | S3ObjectType
  | SQSQueueType
  | SSMParameterType
  | SecretsManagerSecretType
  | DynamoDBTableType;

const emit = defineEmits(['openAsset', 'deleteAsset', 'selectAsset']);

const props = defineProps<{
  assetType: AssetConstValuesType;
  assetData: AssetType;
}>();

const viewType = inject('viewType');
const isHoverCard = ref(false);
const assetCardRef = ref();
const isSelected = ref(false);

const assetName = computed(
  () =>
    props.assetData[
      ASSET_DATA_NAME[
        props.assetType as keyof typeof ASSET_DATA_NAME
      ] as keyof AssetType
    ]
);

const assetDataDisplay = computed(() => {
  const nameKey =
    ASSET_DATA_NAME[props.assetType as keyof typeof ASSET_DATA_NAME];

  return Object.entries(props.assetData)
    .map(([key, value]) => {
      if (key.includes(nameKey)) return null;
      if (Array.isArray(value)) return [key, value.length];
      return [key, value];
    })
    .filter((asset) => asset !== null);
});

const assetLabel = computed(() => {
  return ASSET_TYPE_LABEL[props.assetType as keyof typeof ASSET_TYPE_LABEL];
});

function showDataLabel(key: keyof typeof ASSET_DATA_LABEL) {
  return ASSET_DATA_LABEL[key];
}

function showDataIcon(key: string) {
  return ASSET_WITH_ICON.includes(key);
}

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

function handleSelectAsset(value: boolean) {
  isSelected.value = value;
  emit('selectAsset', isSelected.value);
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
.asset-card__wrapper.gridView {
  position: relative;
  display: flex;
  align-items: stretch;

  .asset-card {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    justify-content: space-between;
    align-items: stretch;

    &__content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8;
      padding-inline: 0.5rem;
      padding-top: 0.5rem;

      img {
        height: 2rem;
        width: 2rem;
        border-radius: 2rem;
      }

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
          display: flex;
          flex-direction: row;
          gap: 0.3rem;
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

.asset-card__wrapper.listView {
  display: flex;
  position: relative;

  .asset-card {
    display: flex;
    flex-grow: 1;
    gap: 0.5rem;
    padding-block: 0.5rem;
    padding-inline: 0.5rem;

    @media (max-width: 1024px) {
      flex-direction: column;
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

        span.value {
          gap: 0.3rem;
          display: flex;
          flex-direction: row;
        }
      }

      li:not(:last-child) {
        border-right: 1px solid hsl(153, 9%, 81%);

        @media (max-width: 768px) {
          border: none;
        }
      }
    }

    &__btn-edit {
      display: none;
    }

    &__options {
      display: none;
      align-items: center;

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
