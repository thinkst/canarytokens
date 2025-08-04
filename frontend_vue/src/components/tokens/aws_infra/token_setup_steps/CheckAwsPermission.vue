<template>
  <section class="flex text-center flex-col">
    <div class="infra-token__title-wrapper flex flex-col items-center">
      <h2>
        {{ isLoading ? 'Checking permission...' : `Check your AWS permission` }}
      </h2>
    </div>
    <div class="flex justify-center">
      <StepState
        v-if="isLoading"
        class="mb-24 sm:w-[100%] md:max-w-[60vw] lg:max-w-[50vw]"
        :is-loading="isLoading"
      >
        <template #loading>
          <GenerateLoadingState
            :instructions="[
              'AWS account found',
              'Verifying permissions',
              'Analysing cloud account',
            ]"
            img-src="aws_infra_token_loading_scanner.webp"
          /> </template
      ></StepState>
    </div>
    <div
      v-if="!isLoading"
      class="flex flex-col text-left items-center"
    >
      <BaseMessageBox
        class="mb-24 sm:w-[100%] md:max-w-[60vw] lg:max-w-[50vw]"
        variant="warning"
        >In order to proceed we need you to confirm the
        <span class="font-semibold">External ID</span> for our role on your AWS
        Account <span class="font-semibold">{{ accountNumber }}</span
        >.
      </BaseMessageBox>
      <div class="text-left max-w-[100%]">
        <BaseSkeletonLoader
          v-if="isLoadingSnippet"
          class="w-[100%] h-[300px] mb-24"
          type="text"
        />
        <BaseCard
          v-else
          class="p-40 flex items-center flex-col text-left sm:max-w-[100%] md:max-w-[60vw] lg:max-w-[50vw] place-self-center"
        >
          <div class="text-center mb-24">
            <h2 class="text-2xl mb-16">
              Run the AWS CLI command below to
              <span class="font-semibold">find the External ID</span>
            </h2>
          </div>
          <BaseLabelArrow
            id="aws-snippet-code"
            label="Copy AWS CLI snippet"
            arrow-word-position="last"
            arrow-variant="two"
            class="z-10 text-right"
          />
          <BaseCodeSnippet
            id="aws-snippet-code"
            lang="bash"
            :code="codeSnippetCheckID"
            custom-height="100px"
            class="wrap-code lg:max-w-[50vw]"
            :check-scroll="true"
          />
        </BaseCard>
        <BaseMessageBox
          class="mb-24 mt-24 sm:w-[100%] md:max-w-[60vw] lg:max-w-[50vw]"
          variant="info"
          text-link="Restore Permissions"
          @click="handleModalSetupRolePolicySnippet"
          >Canarytoken IAM role and policy needed. Did you remove them?
        </BaseMessageBox>
        <BaseCard class="p-40 text-left place-self-center w-full mt-24">
          <form
            class="flex flex-col gap-16 items-center"
            @submit="onSubmit"
          >
            <BaseFormTextField
              id="external_id"
              name="external_id"
              label="Add here your External ID"
              placeholder="e.g. abCd7Lb6cEZrMCEm3OAoj"
              required
              :has-arrow="true"
              arrow-variant="one"
              :arrow-word-position="2"
              class="flex-grow external-id-input"
            />
            <BaseMessageBox
              v-if="isError"
              class="mb-24 mt-24 sm:w-[100%] md:max-w-[60vw] lg:max-w-[50vw]"
              variant="danger"
              >{{ errorMessage }}
            </BaseMessageBox>
            <BaseButton
              type="submit"
              variant="primary"
              class="self-center"
              >Check permissions</BaseButton
            >
          </form>
        </BaseCard>
      </div>
    </div>
    <div class="flex justify-center">
      <BaseButton
        v-if="isError"
        class="mt-40"
        variant="secondary"
        @click="handleCheckPermission"
      >
        Try again
      </BaseButton>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, computed, defineAsyncComponent } from 'vue';
import * as Yup from 'yup';
import { useForm } from 'vee-validate';
import { useModal } from 'vue-final-modal';
import type { TokenDataType } from '@/utils/dataService';
import type { TokenSetupData } from '@/components/tokens/aws_infra/types.ts';
import { requestAWSInfraRoleSetupCommands } from '@/api/awsInfra.ts';
import StepState from '../StepState.vue';
import { useFetchUserAccount } from '@/components/tokens/aws_infra/token_setup_steps/useFetchUserAccount.ts';
import {
  StepStateEnum,
  useStepState,
} from '@/components/tokens/aws_infra/useStepState.ts';
import GenerateLoadingState from '@/components/tokens/aws_infra/token_setup_steps/GenerateLoadingState.vue';

const ModalSetupRolePolicySnippet = defineAsyncComponent(
  () =>
    import(
      '@/components/tokens/aws_infra/token_setup_steps/ModalSetupRolePolicySnippet.vue'
    )
);

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  initialStepData: TokenDataType;
  currentStepData: TokenSetupData;
}>();

const { token, auth_token, aws_region, aws_account_number } =
  props.initialStepData;

const accountNumber = ref('');
const accountRegion = ref('');
const roleName = ref('');
const managementAwsAccount = ref('');
const isLoadingSnippet = ref(false);

const stateStatus = ref<StepStateEnum>(StepStateEnum.SUCCESS);
const errorMessage = ref('');
const { isLoading, isError } = useStepState(stateStatus);
const {
  errorMessage: errorMessageFetch,
  stateStatus: stateStatusFetch,
  handleFetchUserAccount,
  proposedPlan,
  availableAiNames,
} = useFetchUserAccount(
  token,
  auth_token,
  computed(() => values.external_id)
);

onMounted(async () => {
  initializeRoleData();
});

async function initializeRoleData() {
  accountNumber.value = aws_account_number;
  accountRegion.value = aws_region;

  const currentAccountInfo =
    props.currentStepData.role_name &&
    props.currentStepData.aws_account &&
    props.currentStepData.aws_account_number;

  currentAccountInfo
    ? ((roleName.value = props.currentStepData.role_name!),
      (managementAwsAccount.value = props.currentStepData.aws_account!),
      (accountNumber.value = props.currentStepData.aws_account_number!))
    : await handleGetRoleName();
}

const codeSnippetCheckID = computed(
  () =>
    `aws iam get-role --role-name ${roleName.value} --query 'Role.AssumeRolePolicyDocument.Statement[0].Condition.StringEquals."sts:ExternalId"' --output text`
);

const schema = Yup.object().shape({
  external_id: Yup.string().required('The external ID is required'),
});

const { handleSubmit, setFieldValue, values } = useForm({
  validationSchema: schema,
  initialValues: {
    external_id: '',
  },
});

async function handleGetRoleName() {
  isLoadingSnippet.value = true;
  errorMessage.value = '';
  try {
    const res = await requestAWSInfraRoleSetupCommands(
      token,
      auth_token,
      accountRegion.value
    );

    if (res.status !== 200 || !res.data.role_setup_commands) {
      stateStatus.value = StepStateEnum.ERROR;
      errorMessage.value =
        res.data.error_message || 'Failed to generate setup commands';
      return;
    }

    roleName.value = res.data.role_setup_commands.role_name;
    managementAwsAccount.value = res.data.role_setup_commands.aws_account;
    stateStatus.value = StepStateEnum.SUCCESS;

    emits('storeCurrentStepData', {
      token,
      auth_token,
      role_name: roleName.value,
      aws_account: managementAwsAccount.value,
      aws_account_number: accountNumber.value,
      is_managing_token: true,
    });
  } catch (err: any) {
    stateStatus.value = StepStateEnum.ERROR;
    errorMessage.value =
      err.data?.message || 'Failed to generate setup commands';
  } finally {
    isLoadingSnippet.value = false;
  }
}

async function handleCheckPermission() {
  errorMessage.value = '';
  stateStatus.value = StepStateEnum.LOADING;

  await handleFetchUserAccount();
}

const onSubmit = handleSubmit(async () => {
  await handleCheckPermission();
});

function handleModalSetupRolePolicySnippet() {
  const { open, close } = useModal({
    component: ModalSetupRolePolicySnippet,
    attrs: {
      roleName: roleName.value,
      externalId: values.external_id,
      managementAwsAccount: managementAwsAccount.value,
      accountNumber: accountNumber.value,
      closeModal: () => {
        close();
      },
      onUpdateExternalId: (newExternalId: string) => {
        setFieldValue('external_id', newExternalId);
      },
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
          role_name: roleName.value,
          aws_account: managementAwsAccount.value,
          aws_account_number: accountNumber.value,
          proposed_plan: proposedPlan.value,
          available_ai_names: availableAiNames.value,
          is_managing_token: true,
        });
        emits('updateStep');
      } else if (newValue === StepStateEnum.ERROR) {
        errorMessage.value = errorMessageFetch.value;
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }
  }
);
</script>

<style scoped>
.wrap-code {
  :deep(pre) > code {
    white-space: pre-wrap;
    word-break: break-word;
  }
}

.external-id-input {
  width: clamp(200px, 100%, 400px);
}
</style>
