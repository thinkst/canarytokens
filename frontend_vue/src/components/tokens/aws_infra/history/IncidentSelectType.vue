<template>
  <section>
    <label for="select_instance_type">Instance type:</label>
    <v-select
      id="select_instance_type"
      v-model="selectedValue"
      class="v-select mt-8"
      :options="options"
      :searchable="false"
      @input="handleSelectOption"
      @option:selected="
        (option: SelectOption) => handleSelectOption(option.value)
      "
    >
      <template #open-indicator="{ attributes }">
        <span v-bind="attributes">
          <font-awesome-icon
            icon="chevron-up"
            class="w-6 h-6 hover:text-grey-400"
        /></span>
      </template>
      <template #option="{ label, value }">
        <div class="flex flex-row items-center gap-16 h-[2rem]">
          <div
            v-if="value"
            :alt="`icon-${value}`"
            :style="{
              backgroundImage: `url(${getImageUrl(`aws_infra_icons/${value}.svg`)})`,
            }"
            class="bg-cover w-[2rem] h-[2rem] duration-100 rounded-full"
          ></div>
          {{ label }}
        </div>
      </template>
      <template #selected-option="{ label, value }">
        <div class="flex flex-row items-center gap-8 h-[1.5rem]">
          <div
            v-if="value"
            :alt="`icon-${value}`"
            :style="{
              backgroundImage: `url(${getImageUrl(`aws_infra_icons/${value}.svg`)})`,
            }"
            class="bg-cover w-[1.5rem] h-[1.5rem] duration-100 rounded-full"
          ></div>
          {{ label }}
        </div>
      </template>
    </v-select>
  </section>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import getImageUrl from '@/utils/getImageUrl';
import {
  AssetTypesEnum,
  ASSET_LABEL,
} from '@/components/tokens/aws_infra/constants.ts';

type SelectOption = { label: string; value: string };

const emits = defineEmits(['selectOption']);

const EMPTY_VALUE = { label: 'Choose asset', value: '' };
const selectedValue = ref(EMPTY_VALUE);

const options = computed(() => {
  return Object.values(AssetTypesEnum)
    .map((val) => {
      return { label: ASSET_LABEL[val], value: val };
    })
    .filter((option) => option !== null);
});

function handleSelectOption(value: string | SelectOption) {
  emits('selectOption', value);
}
</script>

<style lang="scss">
.v-select .vs__search::placeholder {
  @apply text-grey-400;
}
.v-select .vs__dropdown-toggle {
  @apply px-16 py-[0.4rem] border resize-none shadow-inner-shadow-grey rounded-3xl border-grey-400 bg-white outline-offset-1;
}

.v-select .vs__dropdown-menu {
  @apply mt-[8px] bg-white shadow-none border-grey-300 rounded-xl;
  height: var(--vs-dropdown-height);
  border-top-style: solid;
}

.v-select .vs__clear {
  @apply hidden;
}
.v-select .vs__open-indicator {
  @apply fill-grey-400;
}

.v-select .vs__dropdown-option {
  @apply text-grey-500;
}

.v-select .vs__dropdown-option:first-child {
  @apply mt-[0.5rem];
}

.v-select .vs__dropdown-option:last-child {
  @apply mb-[0.5rem];
}

.v-select .vs__dropdown-option--highlight {
  @apply bg-green-500 text-white;
}

.v-select.invalid > .vs__dropdown-toggle {
  @apply border border-red;
}

.vs__selected {
  @apply m-0;
}
</style>
