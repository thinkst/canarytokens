<template>
  <section class="flex text-center flex-col">
    <div class="infra-token__title-wrapper flex flex-col items-center">
      <h2>
        {{ isLoading ? 'Checking permission...' : `Check your AWS permission` }}
      </h2>
      <div v-if="!isLoading && !isError">
        <BaseCard class="p-16 mt-16 flex flex-col gap-8 items-center">
          <img
            :src="getImageUrl('aws_icon.svg')"
            alt="asw-account-icon"
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
      </div>
    </div>
    <div
      v-if="!isLoading && !isError"
      class="flex flex-col text-left items-center"
    >
      <BaseMessageBox
        class="mt-24 mb-24 sm:w-[100%] md:max-w-[60vw] lg:max-w-[50vw]"
        variant="warning"
        >In order to proceed we need you to confirm the <b>External ID</b> for
        our role.</BaseMessageBox
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
    <StepState
      v-if="isLoading || isError"
      :is-loading="isLoading"
      :is-error="isError"
      loading-message="We are checking the permissions, hold on"
      :error-message="errorMessage"
    />
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
import { ref, onMounted } from 'vue';
import * as Yup from 'yup';
import { Form } from 'vee-validate';
import type { TokenDataType } from '@/utils/dataService';
import type { CurrentTokenDataType } from '@/components/tokens/aws_infra/types.ts';
import StepState from '../StepState.vue';
import getImageUrl from '@/utils/getImageUrl.ts';
import {
  StepStateEnum,
  useStepState,
} from '@/components/tokens/aws_infra/useStepState.ts';

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  initialStepData: TokenDataType;
  currentStepData: CurrentTokenDataType;
}>();

const { token, auth_token, aws_region, aws_account_number } =
  props.initialStepData;

const stateStatus = ref<StepStateEnum>(StepStateEnum.SUCCESS);
const errorMessage = ref('');
const { isLoading, isError } = useStepState(stateStatus);

const accountNumber = ref('');
const accountRegion = ref('');

onMounted(async () => {
  accountNumber.value = aws_account_number;
  accountRegion.value = aws_region;
});

const codeSnippetCheckID = `aws iam get-role --role-name Canarytokens-Inventory-ReadOnly-Role --query 'Role.AssumeRolePolicyDocument.Statement[0].Condition.StringEquals."sts:ExternalId"' --output text`;

const schema = Yup.object().shape({
  external_id: Yup.string().required('The external ID is required'),
});

async function handleCheckPermission() {
  errorMessage.value = '';
  stateStatus.value = StepStateEnum.LOADING;
  // ...here goes the API call to manage endpoint...
  emits('updateStep');
}

async function onSubmit() {
  await handleCheckPermission();
}
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
