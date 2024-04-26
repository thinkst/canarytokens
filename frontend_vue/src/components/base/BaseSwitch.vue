<!-- eslint-disable vuejs-accessibility/label-has-for -->
<template>
  <div class="relative flex flex-col justify-between">
    model: {{ model }}
    <input
      v-bind="$attrs"
      :id="id"
      v-model="model"
      type="checkbox"
      role="switch"
      class="toggle"
      :checked="model"
      :aria-checked="model"
    />
    <label
      :for="id"
      class="relative"
      :class="[
        { multiline: helperMessage || errorMessage },
        { loading: loading },
      ]"
      >{{ label }}
      <BaseSpinner
        v-if="loading"
        class="absolute right-[0.6rem]"
        :class="[helperMessage ? 'top-[0.7rem]' : 'top-[0.2rem]']"
        height="1rem"
        :variant="model === true ? 'secondary' : 'primary'"
      ></BaseSpinner>
    </label>
    <div>
      <p
        v-show="helperMessage"
        id="helper"
        class="text-xs leading-4 text-grey-500 pr-[3rem]"
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
defineProps<{
  id: string;
  label: string;
  helperMessage?: string | null;
  errorMessage?: string;
  loading?: boolean;
}>();

const model = defineModel<boolean>();
</script>

<style scoped>
input[type='checkbox'].toggle {
  opacity: 0;
  position: absolute;
  left: -9000px;
  top: -9000px;
}

label {
  position: relative;
  display: flex;
  align-items: center;
}

label:not(.loading) {
  cursor: pointer;
}

label:is(.loading) {
  pointer-events: none;
}

/* toggle wrapper */
label::before {
  content: '';
  position: absolute;
  right: 0;
  width: 2.2em;
  height: 1.4em;
  background-color: hsl(0, 0%, 91%);
  border-radius: 1em;
  transition: background-color 200ms ease-in-out;
}

label.multiline::before {
  top: 0.5rem;
}

label.multiline::after {
  top: 0.75rem;
}

/* toggle ball */
label:not(.loading)::after {
  content: '';
  display: flex;
  position: absolute;
  font-size: 0.5em;
  right: 2.2em;
  width: 1.8em;
  height: 1.8em;
  background-color: hsl(0, 0%, 70%);
  border-radius: 1em;
  transition:
    background-color 150ms ease-in-out,
    transform 100ms ease-in-out,
    height 100ms ease-in-out,
    width 100ms ease-in-out;
}

input[type='checkbox'].toggle:checked + label::before {
  background-color: hsl(152, 59%, 48%);
}

input[type='checkbox'].toggle:checked + label::after {
  transform: translateX(1.9em);
  background-color: white;
}

input[type='checkbox'].toggle:enabled:focus + label::after {
  outline: 0.8em solid hsla(0, 0%, 43%, 0.2);
}

input[type='checkbox'].toggle:enabled:active + label::after {
  outline: 0.8em solid hsla(0, 0%, 43%, 0.2);
  width: 2.1em;
  height: 2.1em;
}

input[type='checkbox'].toggle:checked:disabled + label::before {
  background-color: hsl(152, 59%, 73%);
}

input[type='checkbox'].toggle:disabled + label::before {
  background-color: hsl(0, 0%, 82%);
}

input[type='checkbox'].toggle:disabled + label::after {
  background-color: hsl(0, 0%, 70%);
}

input[type='checkbox'].toggle:disabled + label,
input[type='checkbox'].toggle:checked:disabled + label {
  pointer-events: none;
}
</style>
