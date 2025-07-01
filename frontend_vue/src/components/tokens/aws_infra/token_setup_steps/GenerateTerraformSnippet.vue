<template>
  <section class="section-terraform-snippet flex flex-col items-center">
    <div class="infra-token__title-wrapper text-center">
      <h2>
        {{
          isLoading || isError
            ? 'Preparing the Terraform module...'
            : 'Terraform Module'
        }}
      </h2>
    </div>
    <StepState
      v-if="isLoading || isError"
      :is-loading="isLoading"
      :is-error="isError"
      loading-message="We are generating the terraform module, hold on"
      :error-message="errorMessage"
    />
    <div v-if="isSuccess">
      <h3 class="text-center">
        Add this module to your code and run ``terraform init``
      </h3>
      <BaseCodeSnippet
        lang="bash"
        label="Terraform module"
        :code="terraformSnippet"
        class="mt-40 md:max-w-[600px] max-w-[350px] wrap-code"
        custom-height="150px"
      ></BaseCodeSnippet>
      <div class="flex flex-col items-center pt-16">
        <div class="relative">
          <TokenIcon
            title="aws infra token"
            logo-img-url="aws_infra.png"
            :has-shadow="true"
            class="w-[6rem]"
          />
          <img
            alt="active token"
            :src="getImageUrl('icons/active_token_badge.png')"
            class="absolute top-[4.5rem] left-[4rem] w-[1.5rem]"
          />
        </div>
      </div>
      <h2 class="mt-24 text-center">
        That’s it! Any attempts to interact with the decoy assets will generate
        an alert.
      </h2>
    </div>
    <div class="flex flex-row mt-40 gap-16">
      <BaseButton
        v-if="!isLoading"
        variant="secondary"
        @click="router.push('/')"
      >
        Back Home</BaseButton
      >
      <BaseButton
        v-if="!isLoading"
        variant="secondary"
        @click="handleManageTokenButton"
      >
        Manage Token</BaseButton
      >
    </div>
    <BaseButton
      v-if="isError"
      class="mt-40"
      variant="secondary"
      @click="handleRequestTerraformSnippet"
    >
      Try again
    </BaseButton>
  </section>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import getImageUrl from '@/utils/getImageUrl';
import type { TokenDataType } from '@/utils/dataService';
import { TOKENS_TYPE } from '@/components/constants.ts';
import { requestTerraformSnippet } from '@/api/awsInfra.ts';
import { launchConfetti } from '@/utils/confettiEffect';
import StepState from '../StepState.vue';
import TokenIcon from '@/components/icons/TokenIcon.vue';
import {
  StepStateEnum,
  useStepState,
} from '@/components/tokens/aws_infra/useStepState.ts';

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  initialStepData: TokenDataType;
}>();

const router = useRouter();
const stateStatus = ref<StepStateEnum>(StepStateEnum.LOADING);
const { isLoading, isError, isSuccess } = useStepState(stateStatus);
const errorMessage = ref('');

const terraformSnippet = ref('');

const { token, auth_token } = props.initialStepData;

onMounted(async () => {
  await handleRequestTerraformSnippet();
});

async function handleRequestTerraformSnippet() {
  const POLL_INTERVAL = 2000;
  errorMessage.value = '';
  stateStatus.value = StepStateEnum.LOADING;

  try {
    const res = await requestTerraformSnippet({
      canarytoken: token,
      auth_token,
    });
    if (res.status !== 200) {
      stateStatus.value = StepStateEnum.ERROR;
      errorMessage.value = res.data.message;
    }

    const handle = res.data.handle;

    const startTime = Date.now();
    const timeout = 5 * 60 * 1000; // 5 minutes

    const pollTerraformSnippet = async () => {
      try {
        const resWithHandle = await requestTerraformSnippet({ handle });

        if (resWithHandle.status !== 200) {
          stateStatus.value = StepStateEnum.ERROR;
          errorMessage.value =
            resWithHandle.data.error ||
            'Error on requesting the Terraform Snippet';
          clearInterval(pollingTerraformSnippetInterval);
          return;
        }

        if (resWithHandle.data.message) {
          stateStatus.value = StepStateEnum.ERROR;
          errorMessage.value = resWithHandle.data.message;
          clearInterval(pollingTerraformSnippetInterval);
          return;
        }

        // timeout
        if (Date.now() - startTime >= timeout) {
          stateStatus.value = StepStateEnum.ERROR;
          errorMessage.value = 'The operation took too long. Try again.';
          clearInterval(pollingTerraformSnippetInterval);
          return;
        }

        // success
        if (resWithHandle.data.terraform_module_snippet) {
          stateStatus.value = StepStateEnum.SUCCESS;
          const terraform_module_snippet =
            resWithHandle.data.terraform_module_snippet;

          terraformSnippet.value = terraform_module_snippet;
          emits('storeCurrentStepData', {
            token,
            auth_token,
            terraform_module_snippet,
          });
          clearInterval(pollingTerraformSnippetInterval);
          return;
        }
      } catch (err: any) {
        stateStatus.value = StepStateEnum.ERROR;
        errorMessage.value =
          err.message || 'An error occurred while checking the Role. Try again';
        clearInterval(pollingTerraformSnippetInterval);
        return;
      }
    };

    const pollingTerraformSnippetInterval = setInterval(
      pollTerraformSnippet,
      POLL_INTERVAL
    );
  } catch (err: any) {
    stateStatus.value = StepStateEnum.ERROR;
    errorMessage.value = err.message;
  }
}

function handleManageTokenButton() {
  router.push({ name: 'manage', params: { auth: auth_token, token } });
}

watch(isSuccess, (newVal) => {
  if (newVal === true) {
    launchConfetti(TOKENS_TYPE.AWS_INFRA, '.section-terraform-snippet');
  }
});
</script>

<style scoped>
.wrap-code {
  :deep(pre) > code {
    white-space: pre-wrap;
    text-align: left;
  }
}
</style>
