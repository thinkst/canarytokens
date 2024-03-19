<!-- eslint-disable vuejs-accessibility/label-has-for -->
<template>
  <div class="flex flex-col-reverse justify-between">
    <input
      v-bind="$attrs"
      :id="id"
      v-model="model"
      type="checkbox"
      role="switch"
      class="toggle"
      :checked="model"
      :aria-checked="model"
      :aria-labelledby="`${id}-label`"
    />
    <label
      v-if="label"
      :for="id"
      >{{ label }}</label
    >
  </div>
</template>

<script setup lang="ts">
defineProps<{
  id: string;
  label?: string;
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
  cursor: pointer;
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

/* toggle ball */
label::after {
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
  cursor: not-allowed;
}
</style>
