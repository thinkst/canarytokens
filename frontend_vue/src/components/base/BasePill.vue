<template>
    <p class="text-xs rounded-xl px-16 py-4 inline-block text-nowrap"
        :class="`bg-${backgroundColour} text-${textColour}`"
    >
        <slot></slot>
    </p>
</template>

<script setup lang="ts">

const props = defineProps({
  backgroundColour: {
    type: String,
    default: 'grey'
  },
  textColour: {
    type: String,
    default: 'white'
  }
});
</script>
