<template>
  <div
    :class="props.disabled ? 'hover:brightness-100' : 'hover:brightness-110'"
    class="relative flex items-center justify-center p-8 duration-100 bg-white border cursor-pointer rounded-2xl border-grey-200"
  >
    <a
      v-bind="$attrs"
      class="bg-cover min-w-[4rem] min-h-[4rem] rounded-2xl duration-100"
      :class="{ 'bg-grey-200 cursor-default': props.disabled }"
      :style="
        !props.disabled && props.url
          ? { backgroundImage: `url(${props.url})` }
          : ''
      "
      :disabled="props.disabled"
      download
      :href="props.url"
    >
      <span class="sr-only">{{ props.alt }} Download</span>
      <span
        :class="{ hidden: props.disabled }"
        class="absolute w-[2rem] rounded-full h-[2rem] bg-green top-[-.5rem] right-[-.5rem] flex items-center justify-center text-white"
        ><font-awesome-icon icon="arrow-down"></font-awesome-icon
      ></span>
    </a>
  </div>
</template>

<script lang="ts" setup>
const props = defineProps<{
  url?: string;
  alt?: string;
  disabled?: boolean;
}>();
</script>
