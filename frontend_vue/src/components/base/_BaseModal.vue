<template>
    <VueFinalModal class="flex items-center justify-center" overlay-class="blur-bg"
        content-class="bg-grey-50 rounded-lg text-grey-800 min-w-96 lg:max-w-[70vw] mx-16 ">
        <!-- header -->
        <div class="relative pt-32 pb-16 bg-white rounded-t-lg header">
            <button type="button" class="absolute top-[52px] left-[30px]" v-if="hasBackButton"
                @click="emit('update:modelValue')">
                <font-awesome-icon icon="angle-left" class="w-6 h-6 hover:text-grey-400" />
            </button>
            <h1 class="pt-16 text-2xl font-semibold text-center">
                {{ title }}
            </h1>
            <button type="button" class="absolute top-[20px] right-[30px]" @click="emit('handleBackButton', false)">
                <font-awesome-icon icon="xmark" class="w-6 h-6 hover:text-grey-400" />
            </button>
        </div>

        <!-- content -->
        <div
            class="flex flex-col items-center justify-center px-32 py-16 rounded-b-lg max-w-2lg bg-grey-50 text-grey-800">
            <slot></slot>
        </div>

        <!-- footer -->
        <div class="flex items-center justify-center gap-8 py-24 mt-16 text-center bg-white rounded-b-lg">
            <slot name="footer"></slot>
        </div>

    </VueFinalModal>
</template>

<script setup lang="ts">
import { VueFinalModal } from 'vue-final-modal'

defineProps<{
    hasBackButton: boolean
    title: string
}>()

  const emit = defineEmits<{
  (e: 'update:modelValue'): void, (e: 'handleBackButton', value: false): void,
  }>()


</script>

<style>
.blur-bg {
    background: rgba(149, 149, 149, 0.25) !important;
    backdrop-filter: blur(3px);
}
</style>
