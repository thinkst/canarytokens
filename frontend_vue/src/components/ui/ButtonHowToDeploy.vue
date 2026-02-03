<template>
  <button
    v-tooltip="{
      content: 'How does this work?',
      shown: isOpen,
      triggers: ['hover'],
    }"
    class="w-24 h-24 text-sm duration-150 bg-transparent border border-solid rounded-full hover:text-white hover:bg-green-600 hover:border-green-300"
    :class="[
      size === 'small' ? 'w-[0.5rem] h-[0.5rem]' : 'w-24 h-24',
      isOpen
        ? 'bg-green-600 border-green-300 text-white'
        : 'text-grey-300 border-grey-200',
    ]"
    :aria-label="`How does ${tokenName} work?`"
    @click="emits('click')"
  >
    <font-awesome-icon
      icon="question"
      aria-hidden="true"
    />
  </button>
</template>

<script setup lang="ts">
defineProps<{
  tokenName: string;
  size: 'small' | 'big';
  isOpen?: boolean;
}>();

const emits = defineEmits<{
  (e: 'click'): void;
}>();
</script>
