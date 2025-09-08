<!-- eslint-disable vuejs-accessibility/no-static-element-interactions -->
<!-- eslint-disable vuejs-accessibility/click-events-have-key-events -->
<template>
  <!-- @vue-expect-error content-transition ts error -->
  <VueFinalModal
    overlay-class="blur-bg"
    conten-class="absolute inset-[0px]"
    overlay-transition="vfm-fade"
    :content-transition="modalCustomTransition"
    @update:model-value="(val) => emit('update:modelValue', val)"
  >
    <div
      class="absolute inset-[0px] h-full overflow-auto sm:flex p-16"
      @click.self="handleOverlayClick"
    >
      <div
        class="md:w-[60vw] lg:w-[50vw] mx-auto bg-white rounded-3xl max-w-screen-lg sm:self-center my-auto"
      >
        <!-- Header -->
        <div
          class="relative flex flex-row items-center justify-between px-16 py-24 bg-white rounded-t-3xl header"
        >
          <!-- Button left corner slot -->
          <span class="w-24">
            <slot name="header-btn-left"></slot>
          </span>

          <!-- Modal title -->
          <h1
            class="flex items-center justify-center px-40 text-2xl font-semibold text-center"
          >
            {{ title }}
          </h1>

          <!-- Button right corner slot -->
          <span class="w-24">
            <slot name="header-btn-right"></slot>
          </span>

          <!-- Close 'X' button corner right -->
          <button
            v-if="hasCloseButton"
            type="button"
            class="absolute w-24 h-24 text-sm duration-150 bg-transparent border border-solid rounded-full top-8 right-8 hover:text-white text-grey-300 border-grey-300 hover:bg-green-600 hover:border-green-300"
            @click="emit('update:modelValue', false)"
          >
            <font-awesome-icon
              icon="xmark"
              aria-hidden="true"
            />
            <span class="fa-sr-only">Close</span>
          </button>
        </div>

        <!-- Content -->
        <div
          v-bind="$attrs"
          class="flex flex-col items-center justify-center px-16 py-16 sm:px-32 bg-grey-50 text-grey-800"
          :class="[{ 'pb-24 rounded-b-3xl': hideFooter }, props.contentClass]"
        >
          <!-- Default slot -->
          <slot></slot>

          <!-- ADV banner -->
          <slot name="banner"></slot>
        </div>
        <!-- Footer -->
        <div
          v-if="!hideFooter"
          class="flex items-center justify-center gap-8 py-24 bg-white rounded-b-3xl mb-16text-center"
        >
          <slot name="footer"></slot>
        </div>
      </div>
    </div>
  </VueFinalModal>
</template>

<script setup lang="ts">
import { VueFinalModal } from 'vue-final-modal';

const props = withDefaults(
  defineProps<{
    hasCloseButton: boolean;
    title: string;
    hideFooter?: boolean;
    contentClass?: string;
    clickToClose?: boolean;
  }>(),
  {
    clickToClose: true,
    contentClass: '',
  }
);

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'handleBackButton', value: false): void;
}>();

function handleOverlayClick() {
  if (props.clickToClose) {
    emit('update:modelValue', false);
  }
}

const modalCustomTransition = {
  'enter-active-class': 'ease-out duration-300',
  'enter-from-class': 'opacity-0 ',
  'enter-to-class': 'opacity-100 sm_scale-100',
  'leave-active-class': 'ease-in duration-200',
  'leave-from-class': 'opacity-100 sm_scale-100',
  'leave-to-class': 'opacity-0 ',
};
</script>

<style>
.blur-bg {
  background: rgba(149, 149, 149, 0.25) !important;
  backdrop-filter: blur(3px);
}
</style>
