<template>
  <!-- @vue-expect-error content-transition ts error -->
  <VueFinalModal
    class="flex items-center justify-center modal"
    overlay-class="blur-bg"
    content-class="bg-grey-50 rounded-lg text-grey-800 min-w-96 lg:max-w-[70vw] mx-16"
    overlay-transition="vfm-fade"
    :content-transition="modalCustomTransition"
    esc-to-close
    @update:model-value="(val) => emit('update:modelValue', val)"
  >
    <!-- header -->
    <div class="relative pt-32 pb-16 bg-white rounded-t-lg header">
      <button
        v-if="hasBackButton"
        type="button"
        class="absolute top-[52px] left-[30px]"
        @click="emit('handleBackButton', false)"
      >
        <font-awesome-icon
          icon="angle-left"
          class="w-6 h-6 hover:text-grey-400"
        />
      </button>
      <h1 class="pt-16 text-2xl font-semibold text-center">
        {{ title }}
      </h1>
      <button
        type="button"
        class="absolute top-[20px] right-[30px]"
        @click="emit('update:modelValue', false)"
      >
        <font-awesome-icon
          icon="xmark"
          class="w-6 h-6 hover:text-grey-400"
        />
      </button>
    </div>

    <!-- content -->
    <div
      class="flex flex-col items-center justify-center px-32 py-16 rounded-b-lg max-w-2lg bg-grey-50 text-grey-800"
    >
      <slot></slot>
    </div>

    <!-- footer -->
    <div
      class="flex items-center justify-center gap-8 py-24 mt-16 text-center bg-white rounded-b-lg"
    >
      <slot name="footer"></slot>
    </div>
  </VueFinalModal>
</template>

<script setup lang="ts">
import { VueFinalModal } from 'vue-final-modal';

defineProps<{
  hasBackButton: boolean;
  title: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'handleBackButton', value: false): void;
}>();

const modalCustomTransition = {
  'enter-active-class': 'ease-out duration-300',
  'enter-from-class':
    'opacity-0 translate-y-[-2vh] sm_translate-y-0 sm_scale-95',
  'enter-to-class': 'opacity-100 translate-y-0 sm_scale-100',
  'leave-active-class': 'ease-in duration-200',
  'leave-from-class': 'opacity-100 translate-y-0 sm_scale-100',
  'leave-to-class': 'opacity-0 translate-y-[-2vh] sm_translate-y-0 sm_scale-95',
};
</script>

<style>
.blur-bg {
  background: rgba(149, 149, 149, 0.25) !important;
  backdrop-filter: blur(3px);
}
</style>
