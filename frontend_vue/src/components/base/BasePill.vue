<template>
    <p
        class="text-xs rounded-xl px-16 py-4 inline-block text-nowrap"
        :class="getColourClasses(props.colour)"
    >
        <slot></slot>
    </p>
</template>

<script setup lang="ts">

const props = defineProps({
  colour: {
    type: String,
    default: 'grey'
  },
});

function getColourClasses(colour: string): string {
  switch (colour) {
    case 'grey':
      return 'bg-grey-400 text-white';
    // add more colours here as needed
    default:
      return 'bg-grey-400 text-white';
  }
}

</script>
