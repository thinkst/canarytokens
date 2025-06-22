<template>
  <div class="mb-40 items-center header min-h-[45px] items-stretch">
    <div class="flex mb-[3rem]">
      <BaseButton
        v-if="showBackButton"
        type="button"
        variant="text"
        icon="angle-left"
        @click="handleBackButton"
      >
        Back
      </BaseButton>
    </div>
    <BaseStepCounter
      :steps="stepsValues"
      :current-step="currentStep"
      @handle-step-click="(index: number) => handleChangeStep(index)"
    />
  </div>
  <div class="bg-grey-50 flex flex-col rounded-xl p-16 grow min-h-[40vh]">
    <Suspense>
      <component
        :is="currentComponent"
        v-if="!isInitialError"
        :initial-step-data="sharedData[currentStep - 1]"
        :current-step-data="sharedData[currentStep]"
        @update-step="handleUpdateStep"
        @store-current-step-data="
          (data: GenericDataType) => handleStoreCurrentStepData(data)
        "
        @is-setting-error="(isError: boolean) => handleSettingError(isError)"
        @store-previous-step-data="
          (data: GenericDataType) => handleStorePreviousStepData(data)
        "
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { defineAsyncComponent } from 'vue';
import { useRouter } from 'vue-router';
import { getTokenData } from '@/utils/dataService';
import StepState from './StepState.vue';

const GenerateAwsSnippet = defineAsyncComponent(
  () => import('./token_setup_steps/GenerateAwsSnippet.vue')
);
const CheckAwsPermission = defineAsyncComponent(
  () => import('./token_setup_steps/CheckAwsPermission.vue')
);
const GeneratePlan = defineAsyncComponent(
  () => import('./token_setup_steps/GeneratePlan.vue')
);
const GenerateTerraformSnippet = defineAsyncComponent(
  () => import('./token_setup_steps/GenerateTerraformSnippet.vue')
);

type GenericDataType = {
  [key: string]: string;
};

const props = defineProps<{
  isManageToken?: boolean;
}>();

const router = useRouter();
const currentStep = ref(1);
const sharedData = ref(Array(3).fill({}));
const stepComponents = ref<
  Record<number, ReturnType<typeof defineAsyncComponent>>
>({
  1: props.isManageToken ? CheckAwsPermission : GenerateAwsSnippet,
  2: GeneratePlan,
  3: GenerateTerraformSnippet,
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

const showBackButton = computed(() => {
  return currentStep.value > 1;
});

const stepsValues = [
  { label: 'AWS Setup' },
  { label: 'Plan' },
  { label: 'Terraform snippet' },
];

function handleUpdateStep() {
  currentStep.value++;
}

function handleBackButton() {
  currentStep.value--;
}

function handleChangeStep(index: number) {
  currentStep.value = index;
}

function handleStoreCurrentStepData(data: GenericDataType) {
  sharedData.value[currentStep.value] = data;
}

function handleStorePreviousStepData(data: GenericDataType) {
  sharedData.value[currentStep.value - 1] = {
    ...sharedData.value[currentStep.value - 1],
    ...data,
  };
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
