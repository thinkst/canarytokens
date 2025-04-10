<template>
  <h2 class="step-title">Inventoring Done!</h2>
  <div v-if="isLoading">Loading...</div>

    <p v-if="!isLoading && !isError">
      Next step will be to choose the resources to deploy on your AWS account
    </p>
    <BaseButton
      v-if="!isLoading"
      class="mt-40"
      @click="emits('updateStep')"
    >
      Generate Plan</BaseButton
    >
  </section>
</template>

<script lang="ts" setup>
import { ref } from 'vue';

const emits = defineEmits(['updateStep', 'storeFetchedData']);

const props = defineProps<{
  stepData: any;
}>();

const isLoading = ref(false);
</script>
