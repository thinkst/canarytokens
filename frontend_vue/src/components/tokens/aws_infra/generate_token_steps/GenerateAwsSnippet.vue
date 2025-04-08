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
      loading-message="We are generating the snippet, hold on"
      :error-message="errorMessage"
    />
    <div
      v-else
      class="mt-16 flex items-center flex-col mt-40 text-left"
    >
      <h2 class="font-semibold">Run these commands in your terminal:</h2>
      <BaseCodeSnippet
        v-for="(command, index) in codeSnippetCommands"
        :key="command"
        lang="bash"
        :label="`Command #${index + 1}`"
        :code="formatSnippet(command)"
        custom-height="100px"
        class="md:max-w-[600px] max-w-[350px] mt-16"
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
import { ref, onMounted } from 'vue';
import { requestAWSInfraRoleSetupCommands } from '@/api/main.ts';
import type { tokenDataType } from '@/utils/dataService';
import StepState from '../StepState.vue';

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  stepData: tokenDataType;
}>();

const isLoading = ref(true);
const isError = ref(false);
const errorMessage = ref('');
const codeSnippetCommands = ref<string[]>([]);
const { token, auth_token, aws_region } = props.stepData;

onMounted(async () => {
  await handleGetAwsSnippet();
});

async function handleGetAwsSnippet() {
  isLoading.value = true;
  isError.value = false;
  try {
    const res = await requestAWSInfraRoleSetupCommands(
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
    codeSnippetCommands.value = res.data.role_setup_commands as string[];
    emits('storeCurrentStepData', { token, auth_token });
  } catch (err: any) {
    isError.value = true;
    isLoading.value = false;
    errorMessage.value = err;
  } finally {
    isLoading.value = false;
  }
}

function formatSnippet(snippet: string) {
  // return snippet
  //   .replace(/{/g, '{\n')
  //   .replace(/\s+/g, ' ')
  //   .replace(/ --/g, '\n--');
  return snippet;
}
</script>
