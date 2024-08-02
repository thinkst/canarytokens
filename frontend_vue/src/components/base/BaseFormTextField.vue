<!--
// Component specific for VeeValidate
// https://vee-validate.logaretm.com/v4/examples/custom-inputs/
-->
<template>
  <div
    class="flex flex-col text-grey-800 textfield-wrapper"
    :class="{ 'w-full': fullWidth }"
  >
    <BaseLabel
      v-if="!hasArrow"
      :id="id"
    >
      {{ label }}
    </BaseLabel>
    <BaseLabelArrow
      v-if="hasArrow"
      :id="id"
      :label="label"
      :arrow-variant="arrowVariant"
      :arrow-word-position="arrowWordPosition"
    />
    <component
      :is="inputType"
      :id="id"
      :value="inputValue"
      class="px-16 py-8 border resize-none shadow-inner-shadow-grey rounded-3xl border-grey-400 focus:ring-green-600 focus-visible:ring-1"
      :class="[
        { 'border-red shadow-none': errorMessage },
        { 'border-grey-200 bg-grey-100 shadow-none text-grey-300': disabled },
        { 'hide-scrollbar': multiline },
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
    <div class="h-16 pr-8 mt-4 ml-16">
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
  hasArrow?: boolean;
  arrowVariant?: 'one' | 'two';
  // positions the arrow under the word at the given index
  arrowWordPosition?: number;
  maxLength?: number;
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
<style>
.hide-scrollbar {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* Internet Explorer 10+ */
}
.hide-scrollbar::-webkit-scrollbar {
  /* WebKit */
  width: 0;
  height: 0;
}
</style>
