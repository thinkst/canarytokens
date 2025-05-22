<template>
  <section class="flex text-center flex-col">
    <div class="infra-token__title-wrapper flex flex-col items-center">
      <h2>
        {{ isLoading ? 'Checking permission...' : `Check your AWS permission` }}
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
      </div>
    </div>
    <div v-if="!isLoading && !isError">
      <p class="text-gray-700">
        In order to proceed we need you to confirm the <b>External ID</b> for
        our role.<br />
        Run the AWS CLI command below to find the External ID
      </p>
    </div>
    <div
      v-if="!isLoading && !isError"
      class="flex flex-col text-left items-center"
    >
      <BaseCodeSnippet
        lang="bash"
        label="AWS CLI snippet"
        :code="codeSnippetCheckID"
        custom-height="100px"
        class="mt-24 wrap-code lg:max-w-[50vw]"
        :check-scroll="true"
      />
      <div
        v-if="!isLoading && !isError"
        class="flex flex-col items-stretch sm:min-w-[40vw] md:min-w-[30vw] min-w-full"
      >
        <Form
          class="mt-24 flex flex-col gap-16 items-center"
          :validation-schema="schema"
          @submit="onSubmit"
        >
          <BaseFormTextField
            id="external_id"
            label="Add your External ID"
            placeholder="e.g. abCd7Lb6cEZrMCEm3OAoj"
            required
            class="min-w-full"
          />
          <BaseButton
            type="submit"
            variant="primary"
            >Check permissions</BaseButton
          >
        </Form>
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

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  initialStepData: TokenDataType;
  currentStepData: CurrentTokenDataType;
}>();

const { token, auth_token, aws_region, aws_account_number } =
  props.initialStepData;

const isLoading = ref(false);
const isError = ref(false);
const errorMessage = ref('');
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
  isLoading.value = true;
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
</style>
