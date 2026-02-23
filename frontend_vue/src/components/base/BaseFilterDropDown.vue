<template>
    <div v-clickaway="closePopUp" class="relative" role="menu">
            <BaseButton
            ref="dropdownFilter"
              variant="text"
              icon="filter"
              aria-label="filter button"
                :aria-controls="'alert-filter-dropdown'"
                :aria-expanded="showAlertFilterPopup.toString()"
              @click="showAlertFilterPopup = !showAlertFilterPopup"
              @keydown.escape="closePopUp"
            ></BaseButton>
            <div
              v-if="showAlertFilterPopup"
              class="absolute right-0 top-12 z-20 bg-white border border-grey-200 rounded-lg shadow-lg p-16"
              role="dialog"
              @click.stop
            >
              <fieldset id="radio-group-action" class="space-y-3" role="radiogroup">
                <BaseRadioInput
v-for="option in filterOptions"
                  :id="`${name}-${option}`"
                  :key="option"
                  :name="name"
                  :label="capitalizeOption(option)"
                  :value="option"
                  :checked="filterOption === option"
                  @select-value="handleSelectFilter"
                  @keydown.escape="closePopUp"
                />
              </fieldset>
              </div>
            </div>
</template>
<script setup lang="ts">
import BaseButton from '@/components/base/BaseButton.vue';
import BaseRadioInput from '@/components/base/BaseRadioInput.vue';
import { ref } from 'vue';
import { onClickaway } from '@/directives/clickAway';
import { templateRef } from '@vueuse/core';

const vClickaway = onClickaway;

const props = defineProps<{
  filterOptions: string[];
  defaultFilterOption?: string;
  name: string;
}>();

const emits = defineEmits(['update-filter-option']);

const dropdownFilter = templateRef('dropdownFilter');

const showAlertFilterPopup = ref(false);
const filterOption = ref(props.defaultFilterOption);

function capitalizeOption(option: string) {
  return `${option.charAt(0).toUpperCase()}${option.slice(1)}`;
}

function closePopUp() {
  showAlertFilterPopup.value = false;
  if (dropdownFilter.value && dropdownFilter.value.$el.contains(document.activeElement)) {
    dropdownFilter.value?.$el?.focus();
  }
}

function handleSelectFilter(option: string) {
  filterOption.value = option;
  emits('update-filter-option', option);
}
</script>
