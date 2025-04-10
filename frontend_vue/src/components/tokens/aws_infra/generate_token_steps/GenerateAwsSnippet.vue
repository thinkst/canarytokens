<template>
  <section class="w-full flex text-center flex-col items-center">
    <h2 class="step-title">
      {{ isLoading ? 'Generating Snippet...' : 'Generate Snippet' }}
    </h2>
    <div v-if="!isLoading || !isError">
      <p class="text-gray-700">
        To inventory your resources and suggest an optimal plan, we need you to
        create a role in your account.
      </p>
      <p class="text-gray-700 mt-16">
        The following snippet will to create a <b>IAM role</b> and <br />attach
        to it a policy granting <b>read-only access</b> to SQS queues and S3
        buckets.
      </p>
    </div>
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
      <BaseCodeSnippet
        v-for="(command, index) in codeSnippetCommands"
        :key="command"
        lang="bash"
        :label="showSnippetLabel(index)"
        :code="command"
        custom-height="100px"
        class="md:max-w-[600px] max-w-[350px] mt-24 wrap-code"
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

const { token, auth_token, aws_region } = props.stepData;

const isLoading = ref(true);
const isError = ref(false);
const errorMessage = ref('');
const codeSnippetCommands = ref<string[]>([]);

function showSnippetLabel(snippetNumber: number) {
  switch (snippetNumber) {
    case 0:
      return 'Label a new IAM role with trust permissions:';
    case 1:
      return 'Define new policy granting permissions to list SQS queues and S3 buckets:';
    case 2:
      return 'Attach the new policy to then new role:';
    default:
      return '';
  }
}

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

// function formatSnippet(snippet: string) {
// return snippet
//   .replace(/{/g, '{\n')
//   .replace(/\s+/g, ' ')
//   .replace(/ --/g, '\n--');
// }
</script>

<style scoped>
.wrap-code {
  :deep(pre) > code {
    white-space: pre-wrap;
  }
}
</style>
