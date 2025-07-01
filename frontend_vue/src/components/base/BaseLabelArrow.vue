<!-- eslint-disable vue/no-v-html -->
<template>
  <BaseLabel
    v-bind="$attrs"
    :id="id"
    class="container relative mb-8"
  >
    <span v-html="labelArrowed"></span>
  </BaseLabel>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

type ArrowPositionType = number | 'start' | 'last';

const props = defineProps<{
  id: string;
  label: string;
  arrowVariant?: 'one' | 'two';
  arrowWordPosition?: ArrowPositionType;
}>();

const label = ref(props.label);
const arrowVariant = ref(props.arrowVariant) || 'one';

const labelArrowed = computed(() => {
  if (typeof props.arrowWordPosition === 'number') {
    // split the label into words
    const words = label.value.split(' ');
    // add the arrow class to the word at the given index
    const wordsWithArrowclass = words.map((word, index) => {
      if (index + 1 === props.arrowWordPosition) {
        return `<span class="label-arrow label-arrow__${arrowVariant.value}" alt="arrow">${word}</span>`;
      }
      return word;
    });
    // join the words back together
    return wordsWithArrowclass.join(' ');
  }
  if(props.arrowWordPosition === 'last') {
    // split the label into words
    const words = label.value.split(' ');
    // add the arrow class to the end of the label
    const lastWordIndex = words.length - 1;
    words[lastWordIndex] = `<span class="label-arrow label-arrow-last label-arrow__${arrowVariant.value}" alt="arrow">${words[lastWordIndex]}</span>`;
    return words.join(' ');
  }
  if(props.arrowWordPosition === 'start') {
    // split the label into words
    const words = label.value.split(' ');
    // add the arrow class to the beginning of the label
    words[0] = `<span class="label-arrow label-arrow-start label-arrow__${arrowVariant.value}" alt="arrow">${words[0]}</span>`;
    return words.join(' ');
  }
  return label.value;
});
</script>

<style>
.container {
  container-type: inline-size;
}

@container (max-width: 350px) {
  .label-arrow::before {
    display: none;
  }
}

.label-arrow::before {
  content: '';
  height: 1.7rem;
  width: 1.5rem;
  position: absolute;
  top: 1.2rem;
}

.label-arrow-last, .label-arrow-start {
  position: relative;
}

.label-arrow-last::before {
  right: 0;
}

.label-arrow-start::before {
  left: -1rem;
}



.label-arrow__one::before {
  background: url('@/assets/icons/label_arrow_1.svg') no-repeat center / contain;
}

.label-arrow__two::before {
  background: url('@/assets/icons/label_arrow_2.svg') no-repeat center / contain;
}
</style>
