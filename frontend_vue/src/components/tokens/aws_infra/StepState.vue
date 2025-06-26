<template>
  <div class="my-16 flex flex-col items-center">
    <template v-if="isLoading">
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
    <template v-if="isError">
      <h2 class="text-red font-semibold">
        Oh no! Something didn't work as expected
      </h2>
      <img
        v-if="hasIcon"
        :src="getImageUrl('icons/errorIcon.svg')"
        alt="success-icon"
        class="w-[15rem] h-[15rem]"
      />
      <BaseMessageBox
        v-if="errorMessage"
        :message="errorMessage"
        variant="danger"
        class="min-w-[350px] mt-24"
      />
    </template>
    <template v-if="isSuccess && hasIcon">
      <img
        :src="getImageUrl('icons/successIcon.svg')"
        alt="success-icon"
        class="w-[15rem] h-[15rem]"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import getImageUrl from '@/utils/getImageUrl';

const props = defineProps<{
  isLoading?: boolean;
  loadingMessage?: string;
  isError?: boolean;
  errorMessage?: string;
  isSuccess?: boolean;
  successMessage?: string;
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
