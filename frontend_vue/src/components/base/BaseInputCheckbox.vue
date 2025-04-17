<template>
  <label
    v-bind="$attrs"
    :for="props.id"
    :class="[{ 'label-disabled': disabled }]"
  >
    <input
      :id="props.id"
      v-tooltip="
        tooltipContent && {
          content: tooltipContent,
        }
      "
      type="checkbox"
      :disabled="disabled"
      :checked="modelValue"
      @change="handleChange"
    />
    <span :class="[{ 'sr-only': props.hideLabel }]">{{ label }}</span></label
  >
</template>

<script lang="ts" setup>
const props = defineProps<{
  id: string;
  label: string;
  modelValue: boolean;
  hideLabel?: boolean;
  tooltipContent?: string;
  disabled?: boolean;
}>();

const emits = defineEmits(['update:modelValue']);

const handleChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  emits('update:modelValue', target.checked);
};
</script>

<style lang="scss" scoped>
label {
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
  align-items: center;
  color: var(--color-grey-500);

  &:hover {
    color: var(--color-green-700);
  }
}

.label-disabled {
  cursor: not-allowed;
  &:hover {
    color: var(--color-grey-500);
  }
}

input[type='checkbox'] {
  -webkit-appearance: none;
  appearance: none;
  /* For iOS < 15 */
  background-color: white;
  margin: 0;
  font: inherit;
  width: 1rem;
  height: 1rem;
  border: 2px solid var(--color-grey-300);
  border-radius: 1rem;
  transform: translateY(0.1rem);
  display: grid;
  place-content: center;

  &:hover {
    border: 2px solid var(--color-green-700);
  }

  &:checked {
    background-color: var(--color-green-500);
    border: 2px solid var(--color-green-500);
  }

  &:focus-visible {
    outline: max(2px, 0.15em) solid var(--color-green-700);
    outline-offset: max(2px, 0.15em);
  }
  &:disabled {
    color: var(--color-grey-300);
    cursor: not-allowed;
    outline: none;
    border: 2px solid var(--color-grey-300);
    background-color: var(--color-grey-200);
  }
}

input[type='checkbox']::before {
  content: '\f00c';
  font-family: 'Font Awesome 6 Free';
  font-weight: 900;
  font-size: 0.6rem;
  transform: scale(0);
  transform-origin: center;
  transition: 120ms transform ease-in-out;
  color: white;
}

input[type='checkbox']:checked::before {
  transform: scale(1);
}
</style>
