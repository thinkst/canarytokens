<template>
  <div class="flex flex-col items-stretch justify-center w-full">
    <div class="flex flex-col items-center justify-center">
      <span class="relative mb-16">
        <TokenIcon
          :title="tokenServices[props.type].label"
          :logo-img-url="tokenServices[props.type].icon"
          class="h-[6rem] w-[6rem]"
          :has-shadow="true"
          :has-animation="true"
        />
        <img
          :src="getImageUrl(`token_icons/delete_token_badge.png`)"
          :alt="`${tokenServices[props.type].label}`"
          class="absolute w-[1.3rem] bottom-[.5rem] right-[.3rem]"
        />
      </span>
    </div>
    <div
      v-if="!isLoading && !isSuccess"
      class="text-center"
    >
      <p class="text-xl font-semibold leading-normal text-grey-800">
        Are you sure you want to delete this Canarytoken?
      </p>
      <p class="mt-8 leading-normal text-normal text-grey-500">
        All associated alerts will be permanently lost
      </p>
    </div>
    <div
      v-if="isSuccess"
      class="mt-16"
    >
      <BaseMessageBox
        variant="success"
        :message="`The token was deleted successfully. Run the AWS CLI snippet below to remove the role and policy from your AWS account.`"
      ></BaseMessageBox>
      <BaseCodeSnippet
        v-if="codeSnippetCommands"
        lang="bash"
        label="AWS CLI snippet"
        :code="codeSnippetCommands"
        custom-height="100px"
        class="md:max-w-[600px] max-w-[350px] mt-24 wrap-code"
      />
    </div>
    <div
      v-if="isLoading && !isError"
      class="text-center mt-16 flex flex-col items-center"
    >
      <BaseSpinner height="3rem" />
    </div>
    <BaseMessageBox
      v-if="isError && !isSuccess"
      variant="danger"
      class="mt-16"
      :message="isErrorMessage"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { deleteToken } from '@/api/awsInfra';
import { tokenServices } from '@/utils/tokenServices';
import getImageUrl from '@/utils/getImageUrl';
import TokenIcon from '@/components/icons/TokenIcon.vue';

const props = defineProps<{
  auth: string;
  token: string;
  type: string;
  closeModal: () => void;
  triggerDeleteToken: boolean;
}>();

const emits = defineEmits(['tokenDeleted', 'closeModal']);

const isError = ref(false);
const isErrorMessage = ref('');
const isLoading = ref(false);
const isSuccess = ref(false);
const codeSnippetCommands = ref<string>('');

async function deleteTokenFnc() {
  const POLL_INTERVAL = 5000;

  isLoading.value = true;
  isError.value = false;

  try {
    const res = await deleteToken({
      canarytoken: props.token,
      auth_token: props.auth,
    });
    if (res.status !== 200) {
      isLoading.value = false;
      isError.value = true;
      isErrorMessage.value =
        res.data.message ||
        'Error on requesting to delete the token. Try again';
      return;
    }

    const handle = res.data.handle;
    const startTime = Date.now();
    const timeout = 5 * 60 * 1000; // 5 minutes

    const pollDeleteToken = async () => {
      try {
        const resWithHandle = await deleteToken({ handle });

        if (resWithHandle.status !== 200) {
          isLoading.value = false;
          isError.value = true;
          isErrorMessage.value =
            resWithHandle.data.message ||
            'Error on requesting to delete the token. Try again';
          clearInterval(pollingDeleteTokenInterval);
          return;
        }

        // timeout
        if (Date.now() - startTime >= timeout) {
          isLoading.value = false;
          isError.value = true;
          isErrorMessage.value = 'The operation took too long. Try again.';
          clearInterval(pollingDeleteTokenInterval);
          return;
        }

        // success
        if (resWithHandle.data.result === true) {
          isLoading.value = false;
          isSuccess.value = true;
          isError.value = false;

          const customerAwsAccount =
            resWithHandle.data.role_cleanup_commands.customer_aws_account;
          const roleName = resWithHandle.data.role_cleanup_commands.role_name;

          const codeSnippet = generateCodeSnippet(customerAwsAccount, roleName);
          codeSnippetCommands.value = codeSnippet as string;

          clearInterval(pollingDeleteTokenInterval);
          emits('tokenDeleted');
          return;
        }
      } catch (err: any) {
        isError.value = true;
        isErrorMessage.value =
          'Error on requesting to delete the token. Try again';
        clearInterval(pollingDeleteTokenInterval);
        return;
      }
    };

    const pollingDeleteTokenInterval = setInterval(
      pollDeleteToken,
      POLL_INTERVAL
    );
  } catch (err: any) {
    isLoading.value = false;
    isError.value = true;
    isErrorMessage.value = 'Error on requesting to delete the token. Try again';
    isSuccess.value = false;
  }
}

function generateCodeSnippet(customerAwsAccount: number, roleName: string) {
  return `aws iam detach-role-policy --role-name ${roleName} --policy-arn arn:aws:iam::${customerAwsAccount}:policy/Canarytokens-Inventory-ReadOnly-Policy

aws iam delete-policy --policy-arn arn:aws:iam::${customerAwsAccount}:policy/Canarytokens-Inventory-ReadOnly-Policy

aws iam delete-role --role-name  ${roleName}`;
}

watch(
  () => props.triggerDeleteToken,
  (newVal) => {
    if (newVal === true) {
      deleteTokenFnc();
    }
  }
);
</script>
