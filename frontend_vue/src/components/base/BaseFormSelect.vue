<!-- TODO: replace this component with a nicer looking one -->
<template>
  <label
    :for="id"
    class="mt-8 ml-4 font-semibold leading-3"
    >{{ label }}</label
  >
  <select
    :id="id"
    :name="id"
    :value="value"
    class="h-[3rem] rounded-full px-16 border resize-none shadow-inner-shadow-grey border-grey-400 outline-offset-4 m-0"
    @input="handleSelectOption"
    @blur="handleBlur"
  >
    <option
      v-for="option in options"
      :key="option"
      :value="option"
    >
      {{ option }}
    </option>
    <option
      disabled
      value=""
    >
      Select an action
    </option>
  </select>
  <p class="text-xs leading-4 text-red">{{ errorMessage }}</p>
</template>

<script setup lang="ts">
import { toRef } from 'vue';
import { useField } from 'vee-validate';

const props = defineProps<{
  id: string;
  label: string;
  options: string[];
}>();

const id = toRef(props, 'id');
const emits = defineEmits(['selectOption']);

const { value, errorMessage, handleChange, handleBlur } = useField(id);

function handleSelectOption(e: Event) {
  handleChange(e);
  emits('selectOption', (e.target as HTMLSelectElement)?.value);
}
</script>
