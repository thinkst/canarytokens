<template>
  <div class="my-16 flex flex-col items-center">
    <template v-if="isLoading && !$slots.loading">
      <p>{{ loadingMessage }}</p>
      <BaseSpinner
        height="5rem"
        class="mt-24"
      />
      <p class="mt-24">Please don't close this window</p>
      <div
        v-if="isLongLoading"
        class="mt-24"
      >
        <p>This might take up to <b>30 seconds</b></p>
      </div>
    </template>
    <slot v-if="isLoading" name="loading" ></slot>
    <template v-if="isError">
      <img
        v-if="hasIcon"
        :src="getImageUrl('icons/errorIcon.svg')"
        alt="success-icon"
        class="w-[15rem] h-[15rem] mb-24"
      />
      <BaseMessageBox
        v-if="errorMessage"
        :message="errorMessageMapper(errorMessage)"
        variant="danger"
        class="max-w-[100%] md:max-w-[60vw] lg:max-w-[40vw] text-justify"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import getImageUrl from '@/utils/getImageUrl';
import { errorMessageMapper } from '@/utils/errorMessageMapper';

const props = defineProps<{
  isLoading?: boolean;
  loadingMessage?: string;
  isError?: boolean;
  errorMessage?: string;
  hasIcon?: boolean;
}>();

const isLongLoading = ref(false);

watch(
  () => props.isLoading,
  (newVal) => {
    if (newVal === true) {
      setTimeout(() => {
        isLongLoading.value = true;
      }, 30000);
    }
  }
);

watch(
  () => props.isError,
  (newVal) => {
    if (newVal === true) {
      isLongLoading.value = false;
    }
  }
);
</script>
