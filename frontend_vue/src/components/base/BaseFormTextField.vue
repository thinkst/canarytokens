<!-- 
// Component specific for VeeValidate
// https://vee-validate.logaretm.com/v4/examples/custom-inputs/
-->
<template>
  <div
    class="flex flex-col text-grey-800 textfield-wrapper"
    :class="{ 'w-full': fullWidth }"
  >
    <label
      :for="id"
      class="mb-4 ml-4 font-semibold"
      >{{ label }}
      <span
        v-if="required"
        class="text-green-500"
        >*</span
      ></label
    >
    <component
      :is="inputType"
      :id="id"
      :value="inputValue"
      class="px-16 py-8 border resize-none shadow-inner-shadow-grey rounded-3xl border-grey-400 focus:ring-green-600 focus-visible:ring-1"
      :class="[
        { 'border-red shadow-none': errorMessage },
        { 'border-grey-200 bg-grey-100 shadow-none text-grey-300': disabled },
      ]"
      :style="`height: ${multilineHeight}`"
      :placeholder="placeholder"
      :aria-invalid="errorMessage"
      aria-describedby="helper error"
      :required="required"
      :disabled="disabled"
      v-bind="$attrs"
      @blur="handleChange"
      @input="(e: Event) => validateIfErrorExists(e)"
    />
    <div class="pr-8 mt-4 ml-16">
      <p
        v-show="helperMessage"
        id="helper"
        class="text-xs leading-4"
      >
        {{ helperMessage }}
      </p>
      <p
        v-show="errorMessage"
        id="error"
        class="text-xs leading-4 text-red"
      >
        {{ errorMessage }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, toRef } from 'vue';
import { useField } from 'vee-validate';

const props = defineProps<{
  id: string;
  label: string;
  multiline?: boolean;
  helperMessage?: string;
  placeholder?: string;
  required?: boolean;
  multilineHeight?: string;
  fullWidth?: boolean;
  disabled?: boolean;
  value?: string;
}>();

const inputType = computed(() => (props.multiline ? 'textarea' : 'input'));
const id = toRef(props, 'id');

const {
  value: inputValue,
  errorMessage,
  handleChange,
} = useField(id, undefined, {
  initialValue: props.value,
});

// We validate the input on typing only when the field has an error
function validateIfErrorExists(e: Event) {
  if (errorMessage && errorMessage.value) handleChange(e);
}
</script>
