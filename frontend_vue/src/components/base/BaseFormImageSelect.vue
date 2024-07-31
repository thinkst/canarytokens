<template>
  <fieldset>
    <legend class="font-semibold">{{ label }}</legend>
    <div class="flex flex-row flex-wrap items-center justify-center gap-16">
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
            class="bg-cover min-w-[4rem] min-h-[4rem] rounded-2xl duration-100"
            :class="[
              selectedImage === image.value
                ? 'filter-none'
                : 'filter grayscale opacity-40',
              imageClass,
            ]"
            :style="{ backgroundImage: `url(${image.url})` }"
          >
            <span class="sr-only">{{ image.value }}</span>
          </div>
        </label>
      </template>
    </div>
  </fieldset>
</template>

<script setup lang="ts">
import { ref } from 'vue';

type imageType = {
  value: string;
  url: string;
};

defineProps<{
  options: imageType[];
  imageClass?: string;
  label?: string;
}>();

const selectedImage = ref<string>('');

const handleChange = () => {
  console.log(selectedImage.value);
};
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
}

input[type='radio']:focus {
  border: none;
  outline: none;
}

input[type='radio']:checked::after {
  content: '\f00c';
  font-family: 'Font Awesome 6 Free';
  font-weight: 900;
  font-size: 0.6rem;
  position: absolute;
  width: 1.2rem;
  height: 1.2rem;
  top: -5px;
  right: -5px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  @apply bg-green-500;
}
</style>
