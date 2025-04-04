<template>
  <h2 class="step-title">Proposed Plan</h2>
  <div v-if="isLoading">Loading...</div>

  <div>
    <!-- content -->
  </div>

  <BaseButton
    v-if="!isLoading"
    class="mt-40"
    @click="emits('updateStep')"
  >
    Save</BaseButton
  >
</template>

<script lang="ts" setup>
import { ref } from 'vue';

const emits = defineEmits('updateStep', 'storeFetchedData');

const props = defineProps<{
  stepData: any;
}>();

const isLoading = ref(false);
</script>
