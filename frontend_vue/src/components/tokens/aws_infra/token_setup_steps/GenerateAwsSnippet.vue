<template>
  <section class="flex text-center flex-col">
    <div class="infra-token__title-wrapper flex flex-col items-center">
      <h2>
        {{ pageTitle }}
      </h2>
    </div>
    <div class="flex justify-center">
      <StepState
        v-if="!isIdle && !codeSnippetCommands"
        :is-loading="isLoading"
        :is-error="isError"
        loading-message="We are generating the snippet. Hold on…"
        :error-message="errorMessage"
      />
      <StepState
        v-if="!isIdle && codeSnippetCommands"
        class="mb-24 max-w-[100%] md:max-w-[60vw] lg:max-w-[40vw] xl:max-w-[40vw]"
        :is-loading="isLoading"
        :is-error="isError"
        loading-message="This will take a couple of seconds for us to analyse your account, depending on network conditions, solar flare activity, and errant squirrels. Hold on…"
        :error-message="errorMessage"
        :has-icon="false"
        :has-error-title="false"
      />
    </div>
    <div
      v-if="!isLoading && codeSnippetCommands"
      class="flex flex-col items-center"
    >
      <div class="text-left max-w-[100%]">
        <BaseCard
          class="p-40 pt-24 flex items-center flex-col text-left max-w-[100%] md:max-w-[60vw] lg:max-w-[40vw] xl:max-w-[40vw] place-self-center"
        >
          <div class="text-center mb-24">
            <div class="flex justify-center mb-24">
              <TokenIcon
                title="aws infra token"
                logo-img-url="aws_infra.png"
                :has-shadow="true"
                class="w-[5rem]"
              />
            </div>
            <h2 class="text-2xl mb-16">Execute the AWS CLI snippet below</h2>
            <p>
              We need to inventory your account to suggest decoy resources to
              deploy, execute these commands to give us read-only access.
            </p>
          </div>
          <BaseLabelArrow
            id="aws-snippet"
            label="Copy AWS CLI snippet"
            arrow-word-position="last"
            arrow-variant="two"
            class="z-10 text-right"
          />
          <BaseCodeSnippet
            v-if="codeSnippetCommands"
            id="aws-snippet"
            lang="bash"
            :code="codeSnippetCommands"
            custom-height="120px"
            class="wrap-code max-w-[100%]"
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
        <div class="mt-24 flex flex-col items-center">
          <BaseMessageBox
            class="mb-24 max-w-[100%] md:max-w-[60vw] lg:max-w-[40vw] xl:max-w-[40vw] text-justify"
            variant="info"
            >Please ensure you have run the above commands on the
            <span class="font-bold">{{ accountNumber }}</span> AWS account
            <button
              class="font-semibold"
              @click.stop="handleChangeAccountValues"
            >
              (edit)
            </button>
            before continuing, otherwise the setup won’t work.
          </BaseMessageBox>
        </div>
        <div
          v-if="isIdle"
          class="flex flex-col items-center"
        >
          <BaseMessageBox
            v-if="showWarningSnipeptCheck"
            variant="warning"
            class="mb-24 max-w-[100%] md:max-w-[60vw] lg:max-w-[40vw] xl:max-w-[40vw] text-justify"
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
        variant="secondary"
        @click="handleGetAwsSnippet"
      >
        Try again
      </BaseButton>
      <div v-if="isError && codeSnippetCommands">
        <BaseButton
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
import TokenIcon from '@/components/icons/TokenIcon.vue';
import type { TokenDataType } from '@/utils/dataService';
import type { TokenSetupDataType } from '@/components/tokens/aws_infra/types.ts';
import StepState from '../StepState.vue';
import type { GenericObject } from 'vee-validate';
import {
  StepStateEnum,
  useStepState,
} from '@/components/tokens/aws_infra/useStepState.ts';
import { useFetchUserAccount } from '@/components/tokens/aws_infra/token_setup_steps/useFetchUserAccount.ts';
import { policyDocument } from '@/components/tokens/aws_infra/constants.ts';

const ModalInfoSnippet = defineAsyncComponent(
  () => import('./ModalInfoSnippet.vue')
);

const ModalEditAWSInfo = defineAsyncComponent(
  () => import('./ModalEditAWSInfo.vue')
);

const emits = defineEmits([
  'updateStep',
  'storeCurrentStepData',
  'storePreviousStepData',
]);

const props = defineProps<{
  initialStepData: TokenDataType;
  currentStepData: TokenSetupDataType;
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
    return 'Analysing your AWS account';
  } else {
    return 'Setup AWS role and policy';
  }
});
const codeSnippetCommands = ref<string>('');
const accountNumber = ref('');
const accountRegion = ref('');
const managementAwsAccount = ref<number>(0);
const roleName = ref('');
const externalId = ref('');

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

    managementAwsAccount.value = res.data.role_setup_commands.aws_account;
    externalId.value = res.data.role_setup_commands.external_id;
    roleName.value = res.data.role_setup_commands.role_name;

    const codeSnippet = generateCodeSnippet();

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
  codeSnippetCommands.value  = generateCodeSnippet();
  emits('storeCurrentStepData', {
      token,
      auth_token,
      code_snippet_command: codeSnippetCommands.value,
    });
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

function handleChangeAccountValues() {
  const { open, close } = useModal({
    component: ModalEditAWSInfo,
    attrs: {
      closeModal: () => close(),
      saveData: (data: GenericObject) => handleSaveEditData(data),
      tokenData: props.initialStepData,
    },
  });
  open();
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
        window.scrollTo({ top: 0, behavior: 'smooth' });
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
) {
  return `aws iam create-role --no-cli-pager --role-name ${roleName.value} --assume-role-policy-document \'{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"AWS": "arn:aws:sts::${managementAwsAccount.value}:assumed-role/InventoryManagerRole/${externalId.value}"}, "Action": "sts:AssumeRole", "Condition": {"StringEquals": {"sts:ExternalId": "${externalId.value}"}}}]}\'

aws iam create-policy --no-cli-pager --policy-name Canarytokens-Inventory-ReadOnly-Policy --policy-document \'${policyDocument}\'

aws iam attach-role-policy --role-name ${roleName.value} --policy-arn arn:aws:iam::${accountNumber.value}:policy/Canarytokens-Inventory-ReadOnly-Policy
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
