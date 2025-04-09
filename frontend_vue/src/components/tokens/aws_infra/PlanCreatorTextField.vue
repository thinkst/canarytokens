<!--
This is a modified copy of the BaseTextField component.
It exists only for the AWS Infra Token POC.
-->
<template>
  <div
    class="flex flex-col text-grey-800 textfield-wrapper relative"
    :class="{ 'w-full': fullWidth }"
  >
    <BaseLabel :id="id">{{ props.label }}</BaseLabel>
    <input
      v-model="value"
      class="px-16 py-8 border resize-none shadow-inner-shadow-grey rounded-3xl border-grey-400 focus:ring-green-600 focus-visible:ring-1"
      :class="[
        { 'border-red shadow-none': errorMessage },
        { 'border-grey-200 bg-grey-100 shadow-none text-grey-300': disabled },
      ]"
      :placeholder="placeholder"
      :aria-invalid="!!errorMessage"
      aria-describedby="helper error"
      :required="required"
      :disabled="disabled"
      @blur="handleChange"
      @input="(e) => validateIfErrorExists(e)"
    />
    <div class="absolute top-[2rem] right-[0.5rem] flex gap-8">
      <!-- Regenerate content btn -->
      <button
        v-tooltip="{
          content: 'Regenerate content',
        }"
        type="button"
        class="h-[2rem] w-[2rem] rounded-full bg-white hover:bg-green-50 hover:text-green-500 focus:text-green-500 disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none active:top-[0.15rem] focus-visible:outline-0 focus:bg-green-100 focus:border-green-200 focus:outline-0 text-green-600 border border-green-200;"
        aria-label="Regenerate input content"
        @click="emit('handleRegenerateInstance', $event, props.name)"
      >
        <font-awesome-icon
          aria-hidden="true"
          icon="rotate-right"
        ></font-awesome-icon>
      </button>
      <!-- Remvoe input btn -->
      <button
        v-if="hasRemove"
        v-tooltip="{
          content: 'Remove input',
        }"
        type="button"
        class="h-[2rem] w-[2rem] rounded-full bg-white hover:bg-red-300 hover:text-white active:shadow-none active:top-[0.15rem] active:text-white focus-visible:outline-0 focus:bg-red-300 focus:text-white focus:border-red focus:outline-0 text-red border border-red;"
        aria-label="Remove input"
        @click="emit('handleRemoveInstance', $event)"
      >
        <font-awesome-icon
          aria-hidden="true"
          icon="xmark"
        ></font-awesome-icon>
      </button>
    </div>
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
import { toRef } from 'vue';
import { useField } from 'vee-validate';

const props = defineProps<{
  id: string;
  name: string;
  label: string;
  helperMessage?: string;
  placeholder?: string;
  required?: boolean;
  fullWidth?: boolean;
  disabled?: boolean;
  maxLength?: number;
  hasRemove?: boolean;
}>();

const emit = defineEmits([
  'update:modelValue',
  'handleRemoveInstance',
  'handleRegenerateInstance',
]);
const name = toRef(props, 'name');

const { value, handleChange, errorMessage } = useField(name);

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
