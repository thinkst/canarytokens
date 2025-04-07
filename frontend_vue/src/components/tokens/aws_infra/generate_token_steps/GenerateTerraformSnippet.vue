<template>
  <h2 class="step-title">Terraform module</h2>
  <h3 class="max-w-[60%] min-w-[350px]">
    Add this module to your code and run ``terraform in it``
  </h3>
  <div v-if="isLoading">Loading...</div>
  <div v-else>
    <BaseCodeSnippet
      lang="bash"
      label="Terraform module"
      :code="placeholderCode"
      class="mt-40"
    ></BaseCodeSnippet>
  </div>
  <h2 class="step-title mt-24">That's all folks!</h2>
  <BaseButton
    v-if="!isLoading"
    class="mt-40"
  >
    Manage Token</BaseButton
  >
  <BaseButton
    v-if="!isLoading"
    class="mt-16"
    variant="secondary"
    @click="router.push('/')"
  >
    Generate new Canarytoken</BaseButton
  >
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps<{
  stepData: any;
}>();

const router = useRouter();
const isLoading = ref(false);
const placeholderCode = 'echo "This is a placeholder command "';
</script>

<style scoped></style>
