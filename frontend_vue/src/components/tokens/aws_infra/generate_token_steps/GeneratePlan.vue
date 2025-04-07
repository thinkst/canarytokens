<template>
  <h2 class="step-title">Proposed Plan</h2>
  <div v-if="isLoading">Loading...</div>

  <PlanCreator v-if="!isLoading" />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { Form } from 'vee-validate';
import PlanCreator from '@/components/tokens/aws_infra/PlanCreator.vue';

const emits = defineEmits('updateStep', 'storeFetchedData');

const props = defineProps<{
  stepData: any;
}>();

const isLoading = ref(false);
</script>
