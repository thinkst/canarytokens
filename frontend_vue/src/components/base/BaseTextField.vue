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
      class="px-16 py-8 border resize-none shadow-inner-shadow-grey rounded-3xl border-grey-400 outline-offset-4"
      :class="[
        { 'border-red shadow-none': hasError },
        { 'border-grey-200 bg-grey-100 shadow-none text-grey-300': disabled },
      ]"
      :style="`height: ${multilineHeight}`"
      :placeholder="placeholder"
      :aria-invalid="hasError"
      aria-describedby="helper error"
      :required="required"
      :disabled="disabled"
      v-bind="$attrs"
      @input="handleChange"
      @blur="handleBlur"
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
  hasError?: boolean;
  // errorMessage?: string;
  helperMessage?: string;
  placeholder?: string;
  required?: boolean;
  multilineHeight?: string;
  fullWidth?: boolean;
  disabled?: boolean;
}>();

// defineModel macro
// doesn't work on Dynamic components :(

const emit = defineEmits(['update:modelValue', 'blur']);
const updateValue = (value: string) => {
  emit('update:modelValue', value);
};

const inputType = computed(() => (props.multiline ? 'textarea' : 'input'));

const id = toRef(props, 'id');

const {
  value: inputValue,
  errorMessage,
  handleBlur,
  handleChange,
  meta,
} = useField(id, undefined, {
  initialValue: props.value,
});
</script>
