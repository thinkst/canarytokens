<template>
  <VueFinalModal class="flex items-center justify-center" overlay-class="blur-bg"
    content-class="bg-white rounded-lg text-grey-800 min-w-96">

    <!-- header -->
    <div class="relative px-32 py-32 header">
      <h1 class="pt-16 text-2xl font-semibold text-center">
        {{ title }}
      </h1>
      <button type="button" class="absolute top-[20px] right-[30px]" @click="emit('confirm')">
        <font-awesome-icon icon="xmark" class="w-6 h-6 hover:text-grey-400" />
      </button>
    </div>

    <!-- content -->
    <div class="px-32 py-32 max-w-2lg bg-grey-50">
      <slot></slot>
    </div>

    <!-- footer -->
    <div class="px-32 py-32 text-center bg-white rounded-lg">
      <slot name="footer"></slot>
    </div>

  </VueFinalModal>
</template>

<script setup lang="ts">
import { VueFinalModal } from 'vue-final-modal'

  defineProps<{
  title?: string
  }>()

  const emit = defineEmits<{
  (e: 'confirm'): void
  }>()

</script>


<style>
.blur-bg {
  background: rgba(149, 149, 149, 0.25) !important;
  backdrop-filter: blur(3px);
}
</style>
