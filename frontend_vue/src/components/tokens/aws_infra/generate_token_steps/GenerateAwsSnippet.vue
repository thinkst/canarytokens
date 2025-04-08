<template>
  <section class="w-full flex text-center flex-col items-center">
    <h2 class="step-title">
      {{ isLoading ? 'Generating Snippet...' : 'Generate Snippet' }}
    </h2>
    <h3
      v-if="!isLoading"
      class="text-gray-700"
    >
      To inventory your resources and suggest an optimal plan, we need you to
      create a role in your account.
    </h3>
    <StepState
      v-if="isLoading || isError"
      :is-loading="isLoading"
      :is-error="isError"
      loading-message="We are checking the role, hold on..."
      :error-message="errorMessage"
    />
    <div
      v-else
      class="mt-16 flex items-center flex-col mt-40"
    >
      <BaseCodeSnippet
        lang="bash"
        label="Run this command in your terminal"
        :code="codeSnippet"
        custom-height="100px"
        class="md:max-w-[60%]"
      />
      <BaseButton
        class="mt-40"
        @click="emits('updateStep')"
      >
        Done, proceed
      </BaseButton>
    </div>
    <BaseButton
      v-if="isError"
      class="mt-40"
      variant="secondary"
      @click="handleGetAwsSnippet"
    >
      Try again
    </BaseButton>
  </section>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue';
import { getAWSinfraRoleSetupCommands } from '@/api/main.ts';
import type { tokenDataType } from '@/utils/dataService';
import StepState from '../StepState.vue';

const emits = defineEmits(['updateStep', 'storeFetchedData']);

const props = defineProps<{
  stepData: tokenDataType;
}>();

const isLoading = ref(true);
const isError = ref(false);
const errorMessage = ref('');
const codeSnippetCommands = ref<string[]>([]);
const { token, auth_token, aws_region } = props.stepData;

const codeSnippet = computed(() => {
  return codeSnippetCommands.value.join('\n');
});

onMounted(async () => {
  await handleGetAwsSnippet();
});

async function handleGetAwsSnippet() {
  isLoading.value = true;
  isError.value = false;
  try {
    const res = await getAWSinfraRoleSetupCommands(
      token,
      auth_token,
      aws_region
    );
    if (res.status !== 200) {
      isLoading.value = false;
      isError.value = true;
      res.data.error_message = errorMessage;
    }
    isLoading.value = false;
    // codeSnippetCommands.value = res.data.role_setup_commands as string[];
    // Mocked value: remove when backend is aligned
    codeSnippetCommands.value = [
      'aws iam create-role --role-name something something',
      'aws iam create-role --role-name something something',
      'aws iam create-role --role-name something something',
    ];
  } catch (err: any) {
    isError.value = true;
    isLoading.value = false;
    errorMessage.value = err;
  } finally {
    isLoading.value = false;
  }
}
</script>
