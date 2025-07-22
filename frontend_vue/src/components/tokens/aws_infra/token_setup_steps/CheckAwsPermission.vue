<template>
  <section class="flex text-center flex-col">
    <div class="infra-token__title-wrapper flex flex-col items-center">
      <h2>
        {{ isLoading ? 'Checking permission...' : `Check your AWS permission` }}
      </h2>
    </div>
   <div class="flex justify-center">
    <StepState
      v-if="isLoading || isError"
      :is-loading="isLoading"
      :is-error="isError"
      loading-message="We are checking the permissions, hold on"
      :error-message="errorMessage"
      class="mb-24 sm:w-[100%] md:max-w-[60vw] lg:max-w-[50vw]"
    />
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
        Account
        <span class="font-semibold">{{ accountNumber }}</span></BaseMessageBox
      >
      <div class="text-left max-w-[100%]">
        <BaseCard
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
            label="AWS CLI snippet"
            :arrow-word-position="3"
            arrow-variant="one"
            class="z-10"
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
        <BaseCard class="p-40 text-left place-self-center w-full mt-24">
          <Form
            class="flex flex-col gap-16 items-center"
            :validation-schema="schema"
            @submit="onSubmit"
          >
            <BaseFormTextField
              id="external_id"
              :value="external_id"
              label="Add here your External ID"
              placeholder="e.g. abCd7Lb6cEZrMCEm3OAoj"
              required
              :has-arrow="true"
              arrow-variant="one"
              :arrow-word-position="2"
              class="flex-grow external-id-input"
            />
            <BaseButton
              type="submit"
              variant="primary"
              class="self-center"
              >Check permissions</BaseButton
            >
          </Form>
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
import { ref, onMounted, watch } from 'vue';
import * as Yup from 'yup';
import { Form } from 'vee-validate';
import type { TokenDataType } from '@/utils/dataService';
import type { GenericObject } from 'vee-validate';
import type { TokenSetupData } from '@/components/tokens/aws_infra/types.ts';
import StepState from '../StepState.vue';
import { useFetchUserAccount } from '@/components/tokens/aws_infra/token_setup_steps/useFetchUserAccount.ts';
import {
  StepStateEnum,
  useStepState,
} from '@/components/tokens/aws_infra/useStepState.ts';

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  initialStepData: TokenDataType;
  currentStepData: TokenSetupData;
}>();

const { token, auth_token, aws_region, aws_account_number } =
  props.initialStepData;

const accountNumber = ref('');
const accountRegion = ref('');
const external_id = ref('')

const stateStatus = ref<StepStateEnum>(StepStateEnum.SUCCESS);
const errorMessage = ref('');
const { isLoading, isError } = useStepState(stateStatus);
const {
  errorMessage: errorMessageFetch,
  stateStatus: stateStatusFetch,
  handleFetchUserAccount,
  proposedPlan,
} = useFetchUserAccount(token, auth_token, external_id);

onMounted(async () => {
  accountNumber.value = aws_account_number;
  accountRegion.value = aws_region;
});

const codeSnippetCheckID = `aws iam get-role --role-name Canarytokens-Inventory-ReadOnly-Role --query 'Role.AssumeRolePolicyDocument.Statement[0].Condition.StringEquals."sts:ExternalId"' --output text`;

const schema = Yup.object().shape({
  external_id: Yup.string().required('The external ID is required'),
});

async function handleGetCheckIDsnippet(){
  // Add code
}

async function handleCheckPermission(){
  errorMessage.value = '';
  stateStatus.value = StepStateEnum.LOADING;
  await handleFetchUserAccount();
}

async function onSubmit(values: GenericObject) {
  external_id.value = values.external_id;
  await handleCheckPermission()
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
          // code_snippet_command: codeSnippetCommands.value,
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
