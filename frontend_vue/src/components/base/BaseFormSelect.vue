<template>
  <label
    :for="id"
    class="mt-8 ml-4 font-semibold leading-3"
    >{{ label }}</label
  >
  <p
    v-if="errorMessage"
    class="text-xs text-red ml-[4px] leading-[0px]"
  >
    {{ errorMessage }}
  </p>
  <v-select
    :id="id"
    class="v-select"
    :options="options"
    :value="value"
    :label="label"
    :searchable="false"
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
  </v-select>
</template>

<script setup lang="ts">
import { toRef, onMounted } from 'vue';
import { useField } from 'vee-validate';

const props = defineProps<{
  id: string;
  label: string;
  options: string[];
  placeholder?: string;
}>();

const id = toRef(props, 'id');
const emits = defineEmits(['selectOption']);

const { value, errorMessage, handleChange, handleBlur } = useField(id);

onMounted(() => {
  // When selecting the v-select, focus is set on the inner search input
  // This function toggle the 'focus-visible' class on the parent wrapper
  const innerEl = document.querySelector('.vs__search');
  innerEl?.addEventListener('focusin', setParentFocus);
  innerEl?.addEventListener('blur', setParentFocus);

  function setParentFocus() {
    const parentEl = document.querySelector('.vs__dropdown-toggle');
    parentEl?.classList.toggle('focus-visible');
  }
});

function handleSelectOption(value: string) {
  handleChange(value);
  emits('selectOption', value);
}
</script>

<style>
.focus-visible {
  outline: 2px solid;
  outline-color: hsl(191, 96%, 36%);
}

.v-select .vs__search::placeholder {
  @apply text-grey-400;
}
.v-select .vs__dropdown-toggle {
  @apply px-16 py-8 border resize-none shadow-inner-shadow-grey rounded-xl border-grey-400 bg-white outline-offset-4;
}

.v-select .vs__dropdown-menu {
  @apply mt-[8px] bg-white shadow-none border-grey-100 rounded-b-xl;
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

.v-select .vs__dropdown-option--highlight {
  @apply bg-green-500 text-white;
}
</style>
