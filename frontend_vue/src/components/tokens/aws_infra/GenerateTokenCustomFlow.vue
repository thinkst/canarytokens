<template>
  <div class="w-full mb-40 items-center header min-h-[45px]">
    <div>
      <BaseButton
        v-if="showBackButton"
        type="button"
        variant="secondary"
        icon="angle-left"
        @click="currentStep--"
      >
        Back
      </BaseButton>
    </div>
    <BaseStepCounter
      :steps="5"
      :current-step="currentStep"
      :step-description="stepDescription"
      @handle-step-click="(index) => handleChangeStep(index)"
    />
  </div>
  <Suspense>
    <component
      :is="currentComponent"
      v-if="!isInitialError"
      :step-data="sharedData[currentStep - 1]"
      @update-step="handleUpdateStep"
      @store-current-step-data="
        (data: GenericDataType) => handleStoreCurrentStepData(data)
      "
      @is-setting-error="(isError: boolean) => handleSettingError(isError)"
    />
    <template #fallblack>
      <p>Loading next step...</p>
    </template>
  </Suspense>
  <StepState
    v-if="isInitialError"
    :is-error="isInitialError"
    error-message="We couldn't start the process. You'll be redirected to the Home Page."
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { defineAsyncComponent } from 'vue';
import { useRouter } from 'vue-router';
import { getTokenData } from '@/utils/dataService';
import StepState from './StepState.vue';
const GenerateAwsSnippet = defineAsyncComponent(
  () => import('./generate_token_steps/GenerateAwsSnippet.vue')
);
const CheckAwsRole = defineAsyncComponent(
  () => import('./generate_token_steps/CheckAwsRole.vue')
);
const InventoryAwsAccount = defineAsyncComponent(
  () => import('./generate_token_steps/InventoryAwsAccount.vue')
);
const GeneratePlan = defineAsyncComponent(
  () => import('./generate_token_steps/GeneratePlan.vue')
);
const GenerateTerraformSnippet = defineAsyncComponent(
  () => import('./generate_token_steps/GenerateTerraformSnippet.vue')
);

type GenericDataType = {
  [key: string]: string;
};

const router = useRouter();
const currentStep = ref(1);
const sharedData = ref(Array(5).fill({}));
const stepComponents = ref<
  Record<number, ReturnType<typeof defineAsyncComponent>>
>({
  1: GenerateAwsSnippet,
  2: CheckAwsRole,
  3: InventoryAwsAccount,
  4: GeneratePlan,
  5: GenerateTerraformSnippet,
});
const isInitialError = ref(false);
const isSettingError = ref(false);

onMounted(() => {
  sharedData.value[0] = getTokenData();
  if (sharedData.value[0] === null) {
    isInitialError.value = true;
    setTimeout(() => {
      router.push('/');
    }, 5000);
  }
});

const currentComponent = computed(
  () => stepComponents.value[currentStep.value] || null
);

// TODO: check if we can or want user to go back to initial snippets
// Because to re-check the role they might need to manually remove the existing role/user
const showBackButton = computed(() => {
  return (
    currentStep.value > 2 || (currentStep.value === 2 && isSettingError.value)
  );
});

const stepDescription = [
  'Generate AWS snippet',
  'Check AWS role',
  'Inventory AWS account',
  'Generate Plan',
  'Terraform Snippet',
];

function handleUpdateStep() {
  currentStep.value++;
}

function handleStoreCurrentStepData(data: GenericDataType) {
  sharedData.value[currentStep.value] = data;
}

function handleChangeStep(index: number) {
  currentStep.value = index;
}

function handleSettingError(isError: boolean) {
  isSettingError.value = isError;
}
</script>

<style>
.infra-token__title-wrapper {
  margin-top: 1rem;
  margin-bottom: 1.5rem;

  h2 {
    font-size: 2rem;
    text-align: center;
  }
}

.header {
  display: grid;
  grid-template-columns: 1fr 3fr 1fr;
}
</style>
