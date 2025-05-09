<template>
  <label
    :for="id"
    class="mt-8 ml-4 font-semibold"
    >{{ label }}</label
  >

  <v-select
    :id="id"
    v-model="selectedOption"
    class="v-select"
    :class="{ invalid: errorMessage }"
    :style="`--vs-dropdown-height: ${props.height}`"
    :options="options"
    :searchable="searchable"
    :placeholder="placeholder"
    @input="handleSelectOption"
    @blur="handleBlur"
    @option:selected="(value: string) => handleSelectOption(value)"
  >
    <template #open-indicator="{ attributes }">
      <span v-bind="attributes">
        <font-awesome-icon
          icon="chevron-up"
          class="w-6 h-6 hover:text-grey-400"
      /></span>
    </template>
    <template #option="option">
      <slot
        name="option"
        :option="option"
        :value="option.value"
      >
      </slot>
    </template>
    <template #selected-option="option">
      <slot
        name="selected-option"
        :option="option"
        :value="option.value"
      ></slot>
    </template>
  </v-select>
  <div class="h-8 mt-8 ml-16">
    <p
      v-if="errorMessage"
      class="text-xs text-red leading-[0px]"
    >
      {{ errorMessage }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { toRef, onMounted, ref, computed } from 'vue';
import { useField } from 'vee-validate';

export type SelectOption = { label: string; value: string };

const props = defineProps<{
  id: string;
  label: string;
  options: string[] | SelectOption[];
  placeholder?: string;
  searchable?: boolean;
  height?: string;
  value?: string | SelectOption;
}>();

const id = toRef(props, 'id');
const emits = defineEmits(['selectOption']);
const selectedOption = ref();

const initialValueFormatted = computed(() => {
  if (props.value && typeof props.value === 'object') {
    return props.value.value;
  }
  return '';
});

const { errorMessage, handleChange, handleBlur } = useField(id, undefined, {
  initialValue: initialValueFormatted,
});

onMounted(async () => {
  // When selecting the v-select, focus is set on the inner search input
  // This function toggle the 'focus-visible' class on the parent wrapper
  const innerEl = document.querySelector('.vs__search');
  innerEl?.addEventListener('focusin', setParentFocus);
  innerEl?.addEventListener('blur', setParentFocus);

  function setParentFocus() {
    const parentEl = document.querySelector('.vs__dropdown-toggle');
    parentEl?.classList.toggle('focus-visible');
  }

  if (props.value) {
    selectedOption.value = props.value;
  }
});

function handleSelectOption(value: string | SelectOption) {
  if (typeof value === 'object') {
    value = value.value;
  }
  handleChange(value);
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
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
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

.vs__selected-options {
  overflow: hidden;
  flex-wrap: nowrap;
  justify-content: flex-start;
}

.vs__selected {
  @apply m-0;
}

.focus-visible {
  outline: 2px solid;
  outline-color: hsl(191, 96%, 36%);
}
</style>