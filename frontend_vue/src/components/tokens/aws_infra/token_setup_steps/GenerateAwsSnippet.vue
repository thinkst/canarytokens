<template>
  <section class="flex text-center flex-col">
    <div class="infra-token__title-wrapper flex flex-col items-center">
      <h2>
        {{ pageTitle }}
      </h2>
    </div>
    <StepState
      v-if="!isIdle && !codeSnippetCommands"
      :is-loading="isLoading"
      :is-error="isError"
      loading-message="We are generating the snippet, hold on"
      :error-message="errorMessage"
    />
    <StepState
      v-if="!isIdle && codeSnippetCommands"
      :is-loading="isLoading"
      :is-error="isError"
      loading-message="We are fetching your account, hold on"
      :error-message="errorMessage"
      :has-icon="false"
    />
    <div
      v-if="!isLoading && codeSnippetCommands"
      class="flex flex-col items-center"
    >
      <div class="flex flex-col items-center mb-16">
        <CardAwsAccount
          :token-data="props.initialStepData"
          @save-edit-data="handleSaveEditData"
        />
      </div>
      <div>
        <BaseMessageBox
          class="mt-24 mb-24 sm:w-[100%] md:max-w-[60vw] lg:max-w-[50vw]"
          variant="info"
          >Please ensure your AWS environment is set up for account
          <span class="font-bold">{{ accountNumber }}</span> before
          continuing.</BaseMessageBox
        >
      </div>
      <div class="text-left max-w-[100%]">
        <BaseCard
          class="p-40 flex items-center flex-col text-left sm:max-w-[100%] md:max-w-[60vw] lg:max-w-[50vw]"
        >
          <div class="text-center">
            <h2 class="text-2xl mb-16">Execute the AWS CLI snippet below</h2>
            <p>
              We need to inventory your account to suggest decoy resources to
              deploy, execute these commands to give us read-only access
            </p>
          </div>
          <BaseCodeSnippet
            v-if="codeSnippetCommands"
            lang="bash"
            label="AWS CLI snippet"
            :code="codeSnippetCommands"
            custom-height="120px"
            class="mt-24 wrap-code max-w-[100%]"
            :check-scroll="true"
            @copy-content="handleSnippetChecked"
            @snippet-scrolled="handleSnippetChecked"
          />
          <div class="text-center flex mt-24 gap-8 items-center justify-center">
            <p>What's this snippet doing?</p>
            <button
              v-tooltip="{
                content: 'Check details',
                triggers: ['hover'],
              }"
              class="w-24 h-24 text-sm duration-150 bg-transparent border border-solid rounded-full hover:text-white hover:bg-green-600 hover:border-green-300"
              aria-label="What's this snippet doing?"
              @click="handleShowModalInfoSnippet"
            >
              <font-awesome-icon
                icon="question"
                aria-hidden="true"
              />
            </button>
          </div>
        </BaseCard>
        <div
          v-if="isIdle"
          class="mt-24 flex flex-col items-center"
        >
          <BaseMessageBox
            v-if="showWarningSnipeptCheck"
            variant="warning"
            class="mb-16"
          >
            Make sure to run the command above. Otherwise, we won't be able to
            generate your canarytoken.
          </BaseMessageBox>
          <BaseButton
            v-if="!showWarningSnipeptCheck"
            @click="handleGoToNextStep"
          >
            Continue
          </BaseButton>
          <BaseButton
            v-if="showWarningSnipeptCheck"
            @click="handleGoToNextStep"
          >
            I Ran the Command, Continue
          </BaseButton>
        </div>
      </div>
    </div>
    <div class="flex justify-center">
      <BaseButton
        v-if="isError && !codeSnippetCommands"
        class="mt-40"
        variant="secondary"
        @click="handleGetAwsSnippet"
      >
        Try again
      </BaseButton>
      <div v-if="isError && codeSnippetCommands">
        <BaseButton
          class="mt-40"
          variant="secondary"
          @click="handleFetchUserAccount"
        >
          Try again
        </BaseButton>
      </div>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, computed, defineAsyncComponent } from 'vue';
import { useModal } from 'vue-final-modal';
import { requestAWSInfraRoleSetupCommands } from '@/api/awsInfra.ts';
import type { TokenDataType } from '@/utils/dataService';
import type { CurrentTokenDataType } from '@/components/tokens/aws_infra/types.ts';
import StepState from '../StepState.vue';
import type { GenericObject } from 'vee-validate';
import {
  StepStateEnum,
  useStepState,
} from '@/components/tokens/aws_infra/useStepState.ts';
import { useFetchUserAccount } from '@/components/tokens/aws_infra/token_setup_steps/useFetchUserAccount.ts';
import { policyDocument } from '@/components/tokens/aws_infra/constants.ts';
import CardAwsAccount from './CardAwsAccount.vue';

const ModalInfoSnippet = defineAsyncComponent(
  () => import('./ModalInfoSnippet.vue')
);

const emits = defineEmits([
  'updateStep',
  'storeCurrentStepData',
  'storePreviousStepData',
]);

const props = defineProps<{
  initialStepData: TokenDataType;
  currentStepData: CurrentTokenDataType;
}>();

const { token, auth_token, aws_region, aws_account_number } =
  props.initialStepData;

const stateStatus = ref<StepStateEnum>(StepStateEnum.LOADING);
const errorMessage = ref('');

const { isLoading, isError } = useStepState(stateStatus);
const {
  errorMessage: errorMessageFetch,
  stateStatus: stateStatusFetch,
  handleFetchUserAccount,
  proposedPlan,
} = useFetchUserAccount(token, auth_token);

const isIdle = computed(
  () =>
    stateStatus.value !== StepStateEnum.LOADING &&
    stateStatus.value !== StepStateEnum.ERROR
);

const pageTitle = computed(() => {
  if (isLoading.value && !codeSnippetCommands.value) {
    return 'Generating AWS Snippet';
  } else if (isLoading.value && codeSnippetCommands.value) {
    return 'Fetching your AWS account';
  } else {
    return 'Setup AWS role and policy';
  }
});
const codeSnippetCommands = ref<string>('');
const accountNumber = ref('');
const accountRegion = ref('');
const isSnippedChecked = ref(false);
const showWarningSnipeptCheck = ref(false);

onMounted(async () => {
  accountNumber.value = aws_account_number;
  accountRegion.value = aws_region;

  const isExistingSnippet = props.currentStepData.code_snippet_command;

  if (isExistingSnippet) {
    codeSnippetCommands.value = isExistingSnippet;
    stateStatus.value = StepStateEnum.SUCCESS;
  } else {
    await handleGetAwsSnippet();
  }
});

async function handleGetAwsSnippet() {
  stateStatus.value = StepStateEnum.LOADING;
  errorMessage.value = '';

  try {
    const res = await requestAWSInfraRoleSetupCommands(
      token,
      auth_token,
      aws_region
    );
    if (res.status !== 200) {
      stateStatus.value = StepStateEnum.ERROR;
      res.data.error_message = errorMessage;
    }
    isLoading.value = false;

    if (!res.data.role_setup_commands) {
      stateStatus.value = StepStateEnum.ERROR;
      errorMessage.value =
        'Something went wrong when we tried to generate your snippet. Please try again.';
    }

    const awsAccount = res.data.role_setup_commands.aws_account;
    const customerAwsAccount =
      res.data.role_setup_commands.customer_aws_account;
    const externalId = res.data.role_setup_commands.external_id;
    const roleName = res.data.role_setup_commands.role_name;

    const codeSnippet = generateCodeSnippet(
      awsAccount,
      customerAwsAccount,
      externalId,
      roleName
    );

    codeSnippetCommands.value = codeSnippet as string;
    stateStatus.value = StepStateEnum.SUCCESS;
    emits('storeCurrentStepData', {
      token,
      auth_token,
      code_snippet_command: codeSnippetCommands.value,
    });
  } catch (err: any) {
    stateStatus.value = StepStateEnum.ERROR;
    errorMessage.value = err;
  }
}

function handleSaveEditData(data: GenericObject) {
  emits('storePreviousStepData', data);
  accountNumber.value = data.aws_account_number;
  accountRegion.value = data.aws_region;
}

function handleSnippetChecked() {
  isSnippedChecked.value = true;
}

async function handleGoToNextStep() {
  if (!isSnippedChecked.value) {
    showWarningSnipeptCheck.value = true;
    isSnippedChecked.value = true;
  } else {
    showWarningSnipeptCheck.value = false;
    await handleFetchUserAccount();
  }
}

watch(
  () => stateStatusFetch.value,
  (newValue) => {
    if (newValue) {
      stateStatus.value = newValue;
      if (newValue === StepStateEnum.SUCCESS) {
        emits('storeCurrentStepData', {
          token,
          auth_token,
          code_snippet_command: codeSnippetCommands.value,
          proposed_plan: proposedPlan.value,
        });
        emits('updateStep');
      } else if (newValue === StepStateEnum.ERROR) {
        errorMessage.value = errorMessageFetch.value;
      }
    }
  }
);

function handleShowModalInfoSnippet() {
  const { open, close } = useModal({
    component: ModalInfoSnippet,
    attrs: {
      closeModal: () => close(),
    },
  });
  open();
}

function generateCodeSnippet(
  awsAccount: number,
  customerAwsAccount: number,
  externalId: string,
  roleName: string
) {
  return `aws iam create-role --no-cli-pager --role-name ${roleName} --assume-role-policy-document \'{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"AWS": "arn:aws:sts::${awsAccount}:assumed-role/InventoryManagerRole/${externalId}"}, "Action": "sts:AssumeRole", "Condition": {"StringEquals": {"sts:ExternalId": "${externalId}"}}}]}\'

aws iam create-policy --no-cli-pager --policy-name Canarytokens-Inventory-ReadOnly-Policy --policy-document \'${policyDocument}\'

aws iam attach-role-policy --role-name ${roleName} --policy-arn arn:aws:iam::${customerAwsAccount}:policy/Canarytokens-Inventory-ReadOnly-Policy
`;
}
</script>

<style scoped>
.wrap-code {
  :deep(pre) > code {
    white-space: pre-wrap;
  }
}
</style>
