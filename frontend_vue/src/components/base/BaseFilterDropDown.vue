<template>
    <div v-clickaway="handleClickAway" class="relative">
            <BaseButton
              ref="filterButton"
              variant="text"
              icon="filter"
              aria-label="filter button"
                :aria-controls="'alert-filter-dropdown'"
                :aria-expanded="showAlertFilterPopup.toString()"
              @click="showAlertFilterPopup = !showAlertFilterPopup"
            ></BaseButton>
            <div
              v-if="showAlertFilterPopup"
              class="absolute right-0 top-12 z-20 bg-white border border-grey-200 rounded-lg shadow-lg p-16"
              role="dialog"
              @click.stop
            >
              <fieldset id="radio-group-action" class="space-y-3">
                <BaseRadioInput
v-for="option in filterOptions"
                  :id="`${name}-${option}`"
                  :key="option"
                  :name="name"
                  :label="option.charAt(0).toUpperCase() + option.slice(1)"
                  :value="option"
                  :checked="filterOption === option"
                  @select-value="handleSelectFilter"
                  @escape="handleClickAway"
                />
              </fieldset>
              </div>
            </div>
</template>
<script setup lang="ts">
import BaseButton from '@/components/base/BaseButton.vue';
import BaseRadioInput from '@/components/base/BaseRadioInput.vue';
import { ref, useTemplateRef } from 'vue';
import { onClickaway } from '@/directives/clickAway';

const vClickaway = onClickaway;
const filterButton = useTemplateRef('filterButton');

const props = defineProps<{
  filterOptions: string[];
  defaultFilterOption?: string;
  name: string;
}>();

const emits = defineEmits(['update-filter-option']);

const showAlertFilterPopup = ref(false);
const filterOption = ref(props.defaultFilterOption);

function handleClickAway() {
  showAlertFilterPopup.value = false;
}

function handleSelectFilter(option: string) {
  filterOption.value = option;
  showAlertFilterPopup.value = false;
  emits('update-filter-option', option);
  filterButton.value?.$el?.focus();
}
</script>
