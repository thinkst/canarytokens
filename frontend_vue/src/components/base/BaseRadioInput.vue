<template>
  <label
    :for="id || name"
    class="flex flex-row text-sm text-grey-400"
  >
    <input
      v-bind="$attrs"
      :id="id"
      type="radio"
      :name="name"
      @change="handleChangeOption"
    />
    {{ label }}</label
  >
</template>

<script lang="ts" setup>
import { watch } from 'vue';
import { useField } from 'vee-validate';

const props = defineProps<{
  id?: string;
  name: string;
  label: string;
}>();

const emits = defineEmits(['hasError', 'selectValue']);
const { value, errorMessage } = useField(props.name);

function handleChangeOption(e: Event) {
  value.value = (e.target as HTMLInputElement).value;
  emits('selectValue', (e.target as HTMLInputElement).value);
}

watch(errorMessage, () => {
  emits('hasError', errorMessage.value);
});
</script>

<style scoped>
/* remove default style */
input[type='radio'] {
  -webkit-appearance: none;
  appearance: none;
  /* For iOS < 15 */
  background-color: #fff;
  /* Not removed via appearance */
  margin: 0;
  font: inherit;
  color: hsl(152, 59%, 48%);
  width: 1rem;
  height: 1rem;
  margin-right: 0.5rem;
  margin-top: 0.25rem;
  border: 0.15rem solid hsl(0, 0%, 82%);
  border-radius: 50%;
  transform: translateY(-0.075em);
  display: grid;
  place-content: center;
}

input[type='radio']::before {
  content: '';
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  transform: scale(0);
  transition: 120ms transform ease-in-out;
  box-shadow: inset 1rem 1rem hsl(152, 59%, 48%);
}

input[type='radio']:checked::before {
  transform: scale(1);
  box-shadow: inset 1rem 1rem hsl(152, 59%, 48%);
}

input[type='radio']:focus {
  outline: max(2px, 0.25rem) solid hsl(148, 68%, 93%);
}

label:has(input[type='radio']:checked) {
  color: hsl(152, 59%, 48%);
}
</style>
