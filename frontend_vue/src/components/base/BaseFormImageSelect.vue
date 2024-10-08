<template>
  <fieldset>
    <legend class="mb-8 font-semibold text-center">{{ label }}</legend>
    <div class="flex flex-row flex-wrap items-center justify-center gap-8">
      <template
        v-for="image in options"
        :key="image.value"
      >
        <label
          :for="image.value"
          :class="
            selectedImage === image.value
              ? ' border-green-500'
              : 'border-grey-200'
          "
          class="relative flex items-center justify-center p-8 duration-100 bg-white border cursor-pointer rounded-2xl"
        >
          <input
            :id="image.value"
            v-model="selectedImage"
            type="radio"
            :value="image.value"
            :aria-checked="selectedImage === image.value"
            @change="handleChange"
          />
          <div
            class="bg-cover min-w-[2.5rem] min-h-[2.5rem] rounded-2xl duration-100"
            :class="[
              selectedImage === image.value ? 'opacity-100' : 'opacity-40',
              imageClass,
            ]"
            :style="{ backgroundImage: `url(${image.url})` }"
          >
            <span class="sr-only">{{ image.value }}</span>
          </div>
        </label>
      </template>
    </div>
    <p
      v-show="errorMessage"
      id="error"
      class="mt-8 text-xs leading-4 text-center text-red"
    >
      {{ errorMessage }}
    </p>
  </fieldset>
</template>

<script setup lang="ts">
import { ref, toRef } from 'vue';
import { useField } from 'vee-validate';

type imageType = {
  value: string;
  url: string;
};

const props = defineProps<{
  id: string;
  options: imageType[];
  imageClass?: string;
  label?: string;
}>();

const emit = defineEmits(['image-selected']);

const selectedImage = ref<string>('');
const id = toRef(props, 'id');

const { value, errorMessage } = useField(id);

const handleChange = () => {
  value.value = selectedImage.value;
  emit('image-selected', selectedImage.value);
};
</script>

<style scoped>
/* remove default style */
input[type='radio'] {
  -webkit-appearance: none;
  appearance: none;
  /* For iOS < 15 */
  background-color: #fff;
  position: absolute;
  opacity: 0;
  /* Not removed via appearance */
  width: 0;
  margin: 0;
}

input[type='radio']:focus {
  border: none;
  outline: none;
}

label:has(input[type='radio']:checked)::after {
  content: '\f00c';
  font-family: 'Font Awesome 6 Free';
  font-weight: 900;
  font-size: 0.6rem;
  @apply bg-green-500 text-white items-center justify-center flex rounded-full absolute w-[1.2rem] h-[1.2rem] top-[-5px] right-[-5px];
}
</style>
