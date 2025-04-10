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
import { ref, computed } from 'vue';
import { defineAsyncComponent } from 'vue';
const GenerateAwsSnippet = defineAsyncComponent(
  () => import('./token_setup_steps/GenerateAwsSnippet.vue')
);
const CheckAwsPermission = defineAsyncComponent(
  () => import('./token_setup_steps/CheckAwsPermission.vue')
);
const CheckAwsRole = defineAsyncComponent(
  () => import('./token_setup_steps/CheckAwsRole.vue')
);
const InventoryAwsAccount = defineAsyncComponent(
  () => import('./token_setup_steps/InventoryAwsAccount.vue')
);
const GeneratePlan = defineAsyncComponent(
  () => import('./token_setup_steps/GeneratePlan.vue')
);
const GenerateTerraformSnippet = defineAsyncComponent(
  () => import('./token_setup_steps/GenerateTerraformSnippet.vue')
);

type GenericFetchedDataType = {
  [key: string]: string;
};

const props = defineProps<{
  tokenData: any;
}>();

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
  'Generate AWS snipper',
  'Check AWS role',
  'Inventory AWS account',
  'Generate Plan',
  'Terraform Snippet',
];

function handleUpdateStep() {
  currentStep.value++;
}

function handleStoreFetchedData(data: GenericFetchedDataType) {
  sharedData.value[currentStep.value - 1] = data;
}

function handleChangeStep(index: number) {
  currentStep.value = index;
}

function handleSettingError(isError: boolean) {
  isSettingError.value = isError;
}
</script>

<style>
.step-title {
  font-size: 2rem;
  margin-bottom: 1.5rem;
  margin-top: 1rem;
  text-align: center;
}

.header {
  display: grid;
  grid-template-columns: 1fr 3fr 1fr;
}
</style>
