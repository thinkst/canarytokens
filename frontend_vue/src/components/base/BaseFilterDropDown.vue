<template>
    <div class="relative">
            <BaseButton
              variant="text"
              icon="filter"
              @click="showAlertFilterPopup = !showAlertFilterPopup"
            ></BaseButton>
            <div
              v-if="showAlertFilterPopup"
              class="absolute right-0 top-12 z-20 w-[6em] bg-white border border-grey-200 rounded-lg shadow-lg p-4"
              @click.stop
            >
              <div id="radio-group-action" class="space-y-3">
                <BaseRadioInput
v-for="option in filterOptions"
                  :id="option"
                  :key="option"
                  :name="name"
                  :label="option.charAt(0).toUpperCase() + option.slice(1)"
                  :value="option"
                  :checked="filterOption === option"
                  @select-value="handleSelectFilter"
                />
              </div>
            </div>
          </div>
</template>
<script setup lang="ts">
import BaseButton from '@/components/base/BaseButton.vue';
import BaseRadioInput from '@/components/base/BaseRadioInput.vue';
import { ref } from 'vue';

const props = defineProps<{
  filterOptions: string[];
  defaultFilterOption?: string;
  name: string;
}>();

const emits = defineEmits(['update-filter-option']);

const showAlertFilterPopup = ref(false);
const filterOption = ref(props.defaultFilterOption);

function handleSelectFilter(option: string) {
  filterOption.value = option;
  showAlertFilterPopup.value = false;
  emits('update-filter-option', option);
}
</script>
