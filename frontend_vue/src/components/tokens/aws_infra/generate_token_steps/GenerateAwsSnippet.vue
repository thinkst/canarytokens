<template>
  <section class="flex text-center flex-col">
    <div class="infra-token__title-wrapper flex flex-col items-center">
      <h2>
        {{
          isLoading ? 'Generating AWS Snippet...' : `Setup AWS role and policy`
        }}
      </h2>
      <BaseCard class="p-16 mt-16 flex flex-col gap-8 items-center">
        <img
          :src="getImageUrl('token_icons/aws_infra.png')"
          alt="asw-token-icon"
          class="w-[4.5rem] h-[4.5rem]"
        />
        <p class="text-md text-grey-400 leading-4">
          AWS account:
          <span class="text-grey font-semibold">{{ accountNumber }}</span>
        </p>
        <p class="text-md text-grey-400 leading-4">
          AWS region:
          <span class="text-grey font-semibold">{{ accountRegion }}</span>
        </p>
      </BaseCard>
      <BaseButton
        variant="text"
        @click="hadnleChangeAccountValues"
        >Incorrect information? Edit</BaseButton
      >
    </div>
    <div v-if="!isLoading || !isError">
      <p class="text-gray-700">
        Ensure your environment is configured to access the AWS account
        <span class="text-grey font-bold">{{ accountNumber }}</span> <br />
        Then run the AWS CLI snippet below
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
      v-if="!isLoading || !isError"
      class="flex items-center flex-col text-left"
    >
      <BaseCodeSnippet
        v-if="codeSnippetCommands.length > 0"
        lang="bash"
        label="AWS CLI snippet"
        :code="handleFormatSnippet(codeSnippetCommands)"
        custom-height="100px"
        class="md:max-w-[600px] max-w-[350px] mt-24 wrap-code"
        :check-scroll="true"
        @copy-content="handleSnippetChecked"
        @snippet-scrolled="handleSnippetChecked"
      />
      <BaseBulletList
        :list="infoList"
        class="md:max-w-[600px] max-w-[350px] mt-24 wrap-code"
      />
      <div>
        <div class="mt-24 flex flex-col items-center">
          <BaseMessageBox
            v-if="showWarningSnipeptCheck"
            variant="warning"
            class="mb-16"
          >
            Make sure to run the command above. Otherwise, the next step will
            lead to an error, preventing you from continuing.
          </BaseMessageBox>
          <BaseButton
            v-if="!showWarningSnipeptCheck"
            @click="handleGoToNextStep"
          >
            Continue
          </BaseButton>
          <BaseButton
            v-if="showWarningSnipeptCheck"
            @click="emits('updateStep')"
          >
            I Ran the Command, Continue
          </BaseButton>
        </div>
      </div>
      {{ codeSnippetCommands.value }}
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
import { ref, onMounted, defineAsyncComponent } from 'vue';
import { requestAWSInfraRoleSetupCommands } from '@/api/main.ts';
import type { TokenDataType } from '@/utils/dataService';
import StepState from '../StepState.vue';
import getImageUrl from '@/utils/getImageUrl.ts';
import { useModal } from 'vue-final-modal';
import ModalEditAWSInfo from '@/components/tokens/aws_infra/generate_token_steps/ModalEditAWSInfo.vue';

// const ModalEditAWSInfo = defineAsyncComponent(
//   () => import('./ModalEditAWSInfo.vue')
// );

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  stepData: TokenDataType;
}>();

const { token, auth_token, aws_region, aws_account_number } = props.stepData;

const isLoading = ref(true);
const isError = ref(false);
const errorMessage = ref('');
const codeSnippetCommands = ref<string[]>([]);
const accountNumber = ref('');
const accountRegion = ref('');
const isSnippedChecked = ref(false);
const showWarningSnipeptCheck = ref(false);

onMounted(async () => {
  accountNumber.value = props.stepData.aws_account_number;
  accountRegion.value = props.stepData.aws_region;
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
    // console.log(codeSnippetCommands.value, 'codeSnippetCommands.value ');
    emits('storeCurrentStepData', { token, auth_token });
  } catch (err: any) {
    isError.value = true;
    isLoading.value = false;
    errorMessage.value = err;
  } finally {
    isLoading.value = false;
  }
}

function hadnleChangeAccountValues() {
  const { open, close } = useModal({
    component: ModalEditAWSInfo,
    attrs: {
      closeModal: () => close(),
      accountNumber: aws_account_number,
      accountRegion: aws_region,
    },
  });
  open();
}

function handleSnippetChecked() {
  isSnippedChecked.value = true;
}

function handleGoToNextStep() {
  if (!isSnippedChecked.value) {
    showWarningSnipeptCheck.value = true;
  } else {
    showWarningSnipeptCheck.value = false;
    emits('updateStep');
  }
}

function handleFormatSnippet(commands: array[]) {
  return commands.join(' ');
}

const infoList = [
  'This step grants Canarytokens.org temporary, read-only access to list names of various AWS resources (S3 buckets, SQS queues, SSM parameters, Secrets Manager secrets, DynamoDB tables, and IAM roles) to create a customized infrastructure plan',
  'This access is automatically revoked by Canarytokens.org after plan creation.',
  'You will be provided with cleanup instructions at the end of the wizard to remove the associated AWS policy, attachment, and role.',
];
</script>

<style scoped>
.wrap-code {
  :deep(pre) > code {
    white-space: pre-wrap;
  }
}
</style>
