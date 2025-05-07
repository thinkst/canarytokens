<template>
  <div class="flex flex-row gap-16">
    <label
      for="Add-new-instance"
      class="mt-8 ml-4 font-semibold"
      >Add
    </label>
    <v-select
      id="Add-new-instance"
      v-model="selectedValue"
      class="v-select min-w-[20rem]"
      :options="options"
      :searchable="false"
      @open="handleResetSelect"
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
            alt="icon"
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
            alt="icon"
            :style="{
              backgroundImage: `url(${getImageUrl(`aws_infra_icons/${value}.svg`)})`,
            }"
            class="bg-cover w-[1.5rem] h-[1.5rem] duration-100 rounded-full"
          ></div>
          {{ label }}
        </div>
      </template>
    </v-select>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import getImageUrl from '@/utils/getImageUrl';
import {
  ASSET_TYPE,
  ASSET_LABEL,
} from '@/components/tokens/aws_infra/constants.ts';

type SelectOption = { label: string; value: string };

const props = defineProps<{
  isTypeMissingPermission: string[];
}>();

const emits = defineEmits(['selectOption']);

const EMPTY_VALUE = { label: 'Choose asset', value: '' };

const selectedValue = ref(EMPTY_VALUE);

const options = computed(() => {
  return Object.values(ASSET_TYPE)
    .map((val) => {
      if (props.isTypeMissingPermission.includes(val)) {
        return null;
      }
      return { label: ASSET_LABEL[val], value: val };
    })
    .filter((option) => option !== null);
});

function handleResetSelect() {
  selectedValue.value = EMPTY_VALUE;
}

function handleSelectOption(value: string | SelectOption) {
  emits('selectOption', value);
}
</script>

<style lang="scss">
.focus-visible {
  outline: 2px solid;
  outline-color: hsl(191, 96%, 36%);
}

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
