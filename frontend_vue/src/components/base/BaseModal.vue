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
      class="absolute inset-[0px] h-full overflow-auto"
      @click.self="() => emit('update:modelValue', false)"
    >
      <div
        class="md:w-[60vw] lg:w-[50vw] my-16 mx-auto bg-white rounded-lg max-w-[900px]"
      >
        <!-- header -->
        <div class="relative pt-32 pb-16 bg-white rounded-t-lg header">
          <button
            v-if="hasBackButton"
            type="button"
            class="absolute top-[40px] left-[30px]"
            @click="emit('handleBackButton', false)"
          >
            <font-awesome-icon
              icon="angle-left"
              class="w-6 h-6 hover:text-grey-400"
              aria-hidden="true"
            />
            <span class="fa-sr-only">Back</span>
          </button>
          <h1
            class="flex items-center justify-center text-2xl font-semibold text-center"
          >
            {{ title }}
            <BaseLinkDocumentation
              v-if="documentationLink"
              :link="documentationLink"
            />
          </h1>
          <button
            type="button"
            class="absolute top-[20px] right-[30px]"
            @click="emit('update:modelValue', false)"
          >
            <font-awesome-icon
              icon="xmark"
              class="w-6 h-6 hover:text-grey-400"
              aria-hidden="true"
            />
            <span class="fa-sr-only">Close</span>
          </button>
        </div>

        <!-- content -->
        <div
          class="flex flex-col items-center justify-center px-8 py-16 sm:px-32 bg-grey-50 text-grey-800"
        >
          <!--default slot -->
          <slot></slot>

          <!-- ADV banner -->
          <slot name="banner"></slot>
        </div>
        <!-- footer -->
        <div
          class="flex items-center justify-center gap-8 py-24 bg-white rounded-b-lg mb-16text-center"
        >
          <slot name="footer"></slot>
        </div>
      </div>
    </div>
  </VueFinalModal>
</template>

<script setup lang="ts">
import { VueFinalModal } from 'vue-final-modal';

defineProps<{
  hasBackButton: boolean;
  title: string;
  documentationLink: string | null;
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
