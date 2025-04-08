<template>
  <div class="mt-24 flex flex-col items-center">
    <template v-if="isLoading">
      <p>{{ loadingMessage }}</p>
      <BaseSpinner height="5rem" />
      <p class="mt-24">Please don't close the window</p>
      <div
        v-if="isLongLoading"
        class="mt-24"
      >
        <p>This might take up to <b>5 minutes</b></p>
      </div>
    </template>
    <template v-if="isError">
      <h2 class="text-red font-semibold">
        Oh no! Something didn't work as expected
      </h2>
      <div class="bg-red rounded-full w-[5rem] h-[5rem] mt-16">
        <font-awesome-icon
          icon="xmark"
          aria-hidden="true"
          class="text-white p-16 text-[3rem] font-semibold"
        />
      </div>
      <BaseMessageBox
        v-if="errorMessage"
        :message="errorMessage"
        variant="danger"
        class="max-w-[50%]"
      />
    </template>
    <template v-if="isSuccess">
      <p>{{ successMessage }}</p>
      <font-awesome-icon
        icon="circle-check"
        aria-hidden="true"
        class="text-green w-[6rem] h-[6rem] mt-24"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{
  isLoading: boolean;
  loadingMessage?: string;
  isError: boolean;
  errorMessage?: string;
  isSuccess?: boolean;
  successMessage?: string;
}>();

const isLongLoading = ref(false);

watch(
  () => props.isLoading,
  (newVal) => {
    if (newVal === true) {
      setTimeout(() => {
        isLongLoading.value = true;
      }, 100000);
    }
  }
);
</script>
