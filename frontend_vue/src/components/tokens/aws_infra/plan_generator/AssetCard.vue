<template>
  <li
    class="asset-card__wrapper"
    :class="viewType"
  >
    <button
      ref="assetCardRef"
      class="asset-card group border group bg-white rounded-2xl top-[0px] shadow-solid-shadow-grey border-grey-200 duration-100 ease-in-out"
      @click.stop="handleClickAsset"
      @mouseover="handleMouseOver"
      @focus="handleMouseOver"
      @mouseleave="handleMouseLeave"
      @blur="handleMouseLeave"
    >
      <!-- Content -->
      <div class="asset-card__content">
        <img
          :src="getImageUrl(`aws_infra_icons/${props.assetType}.svg`)"
          alt="logo-s3-bucket"
          class="rounded-full h-[2.5rem] w-[2.5rem]"
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
          <span class="label text-grey-400">{{ showDataLabel(key) }}:</span>
          <span class="value text-grey-700">{{ value }}</span>
        </li>
      </ul>
      <!--- Btn Edit --->
      <div
        class="asset-card__btn-edit text-sm w-full leading-5 font-semibold border-t-2 border-grey-50 text-grey-700 h-[2rem] rounded-b-2xl transition duration-100 hover-card shadow-solid-shadow-grey"
      >
        {{ isHoverCard ? 'Edit' : assetLabel }}
      </div>
    </button>
    <!-- Select and Btn Delete -->
    <div class="asset-card__options">
      <input
        id="select-asset"
        v-tooltip="{
          content: 'Select asset',
        }"
        type="checkbox"
        class="rounded-full w-[1.5rem]"
      />
      <label
        for="select-asset"
        class="sr-only"
        >Select asset</label
      >
      <button
        v-tooltip="{
          content: 'Delete asset',
        }"
        type="button"
        class="w-[1.5rem] text-grey-300 rounded-full hover:text-green-500"
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

const emit = defineEmits(['saveAsset', 'deleteAsset']);

const props = defineProps<{
  assetData: AssetType;
  assetType: AssetConstValuesType;
}>();

const viewType = inject('viewType');
const isHoverCard = ref(false);
const assetCardRef = ref();

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

function handleClickAsset() {
  // Open Modal
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
    align-items: center;

    &__content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8;
      padding-inline: 1rem;
      padding-top: 0.5rem;

      p {
        padding-block: 0.5rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 20ch;
      }
    }

    &__list-data {
      padding-bottom: 0.5rem;

      li {
        display: flex;
        flex-direction: row;
        gap: 0.5rem;
        justify-content: space-between;

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
      position: absolute;
      //   display: flex;
      justify-content: space-between;
      align-items: center;
      left: 0.5rem;
      right: 0.5rem;
      top: 0.5rem;
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
  .asset-card {
    &__content {
      &__list-data {
      }
    }
    &__btn-edit {
    }
    &__options {
    }
  }
}
</style>
