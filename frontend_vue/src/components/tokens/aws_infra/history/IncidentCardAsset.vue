<template>
  <li class="w-full @container">
    <button
      v-bind="$attrs"
      class="relative w-full px-16 py-8 transition duration-100 bg-white border text-grey-700 grouped group rounded-2xl shadow-solid-shadow-grey border-grey-200 error-card"
      :class="{ 'mb-8': lastKey }"
      @click.stop="handleClickAsset"
    >
      <span class="flex flex-row items-center flex-1 gap-16 ">
        <div
          :alt="`icon-${assetType}`"
          :style="{
            backgroundImage: `url(${getImageUrl(`aws_infra_icons/${assetType}.svg`)})`,
          }"
          class="bg-cover w-[2rem] h-[2rem] duration-100 rounded-full hidden @xs:block min-w-[2rem]"
        ></div>
        <span class="text-left break-all">
          <span
            v-for="(val, key) in assetPreviewInfo"
            :key="key"
            class="block"
          >
            <span
              v-if="val !== null"
              class="capitalize text-grey-400"
              >{{ formatKey(key as string) }}:
            </span>
            <span
              v-if="val !== null"
              class="mr-8 font-semibold"
              >{{ val }}</span
            >
          </span>
        </span>
      </span>
      <span
        class="flex flex-row items-center justify-end gap-8 mt-8 font-semibold text-red sm:hidden"
        >Check Incidents
        <font-awesome-icon
          icon="arrow-right"
          class="text-red"
          aria-hidden="true"
      /></span>
    </button>
  </li>
</template>

<script setup lang="ts">
import getImageUrl from '@/utils/getImageUrl';
import { formatKey } from '@/utils/utils';

type incidentPreviewInfoType = {
  last_date_of_hit: string | Date | null;
  asset_name: string;
  asset_type: string;
};

defineProps<{
  lastKey: boolean;
  assetPreviewInfo: incidentPreviewInfoType;
  assetType: string | undefined;
}>();

const emits = defineEmits(['click']);

function handleClickAsset() {
  emits('click');
}
</script>

<style scoped>
.error-card:hover,
.error-card:focus,
.error-card:active {
  @apply border-green-500  shadow-solid-shadow-green;
}
</style>
