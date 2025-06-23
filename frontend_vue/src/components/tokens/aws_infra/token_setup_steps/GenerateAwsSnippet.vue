<template>
  <section class="flex text-center flex-col">
    <div class="infra-token__title-wrapper flex flex-col items-center">
      <h2>
        {{
          isLoading ? 'Generating AWS Snippet...' : `Setup AWS role and policy`
        }}
      </h2>
      <div v-if="!isLoading && !isError">
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
          @click="hadndleChangeAccountValues"
          >Incorrect information? Edit</BaseButton
        >
      </div>
    </div>
    <div v-if="!isLoading && !isError">
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
      v-if="!isLoading && !isError"
      class="flex items-center flex-col text-left"
    >
      <BaseCodeSnippet
        v-if="codeSnippetCommands"
        lang="bash"
        label="AWS CLI snippet"
        :code="codeSnippetCommands"
        custom-height="100px"
        class="md:max-w-[600px] max-w-[350px] mt-24 wrap-code"
        :check-scroll="true"
        @copy-content="handleSnippetChecked"
        @snippet-scrolled="handleSnippetChecked"
      />
      <BaseBulletList
        v-if="!isLoading && !isError"
        :list="infoList"
        class="md:max-w-[600px] max-w-[350px] mt-24 wrap-code"
      />
      <div v-if="!isLoading && !isError">
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
    </div>
    <div class="flex justify-center">
      <BaseButton
        v-if="isError"
        class="mt-40"
        variant="secondary"
        @click="handleGetAwsSnippet"
      >
        Try again
      </BaseButton>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { ref, onMounted, defineAsyncComponent } from 'vue';
import { requestAWSInfraRoleSetupCommands } from '@/api/awsInfra.ts';
import type { TokenDataType } from '@/utils/dataService';
import type { CurrentTokenDataType } from '@/components/tokens/aws_infra/types.ts';
import StepState from '../StepState.vue';
import getImageUrl from '@/utils/getImageUrl.ts';
import { useModal } from 'vue-final-modal';
import type { GenericObject } from 'vee-validate';
import { StepStateEnum, useStepState } from '@/components/tokens/aws_infra/useStepState.ts';

const ModalEditAWSInfo = defineAsyncComponent(
  () => import('./ModalEditAWSInfo.vue')
);

const emits = defineEmits(['updateStep', 'storeCurrentStepData', 'storePreviousStepData']);

const props = defineProps<{
  initialStepData: TokenDataType;
  currentStepData: CurrentTokenDataType;
}>();

const { token, auth_token, aws_region, aws_account_number } =
  props.initialStepData;

const stateStatus = ref<StepStateEnum>(StepStateEnum.LOADING);
const errorMessage = ref('');
const { isLoading, isError } = useStepState(stateStatus.value);

const codeSnippetCommands = ref<string>('');
const accountNumber = ref('');
const accountRegion = ref('');
const isSnippedChecked = ref(false);
const showWarningSnipeptCheck = ref(false);

const policyDocument =
`{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sqs:ListQueues",
                "sqs:GetQueueAttributes"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:ListTables"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssm:DescribeParameters"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:ListSecrets"
            ],
            "Resource": "*"
        }
    ]
}`

onMounted(async () => {
  accountNumber.value = props.initialStepData.aws_account_number;
  accountRegion.value = props.initialStepData.aws_region;

  const isExistingSnippet = props.currentStepData.codeSnippetCommands;

  if (isExistingSnippet) {
    codeSnippetCommands.value = isExistingSnippet;
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

    emits('storeCurrentStepData', {
      token,
      auth_token,
      codeSnippetCommands: codeSnippetCommands.value,
    });
  } catch (err: any) {
    stateStatus.value = StepStateEnum.ERROR;
    errorMessage.value = err;
  }
}

function hadndleChangeAccountValues() {
  const { open, close } = useModal({
    component: ModalEditAWSInfo,
    attrs: {
      closeModal: () => close(),
      saveData: (data: GenericObject) => handleSaveEditData(data),
      initialStepData: props.initialStepData
    },
  });
  open();
}

function handleSaveEditData(data: GenericObject) {
  emits('storePreviousStepData', data)
  accountNumber.value = data.aws_account_number;
  accountRegion.value = data.aws_region;
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

const infoList = [
  'This step grants Canarytokens.org temporary, read-only access to list names of various AWS resources (S3 buckets, SQS queues, SSM parameters, Secrets Manager secrets, DynamoDB tables, and IAM roles) to create a customized infrastructure plan.',
  'This access is automatically revoked by Canarytokens.org after plan creation.',
  'You will be provided with cleanup instructions at the end of the wizard to remove the associated AWS policy, attachment, and role.',
];

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
