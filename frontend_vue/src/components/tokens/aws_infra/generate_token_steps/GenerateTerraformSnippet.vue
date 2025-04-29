<template>
  <section class="flex text-center flex-col items-center">
    <div class="infra-token__title-wrapper">
      <h2>
        {{
          isLoading || isError
            ? 'Preparing the Terraform module...'
            : 'Terraform Module'
        }}
      </h2>
    </div>
    <StepState
      v-if="isLoading | isError"
      :is-loading="isLoading"
      :is-error="isError"
      loading-message="We are generating the terraform module, hold on"
      :error-message="errorMessage"
    />
    <div v-if="isSuccess">
      <h3>Add this module to your code and run ``terraform init``</h3>
      <BaseCodeSnippet
        lang="bash"
        label="Terraform module"
        :code="terraformSnippet"
        class="mt-40 md:max-w-[600px] max-w-[350px] wrap-code"
        custom-height="150px"
      ></BaseCodeSnippet>
      <div class="flex flex-col items-center pt-16">
        <div class="relative">
          <!-- <img
            alt="aws infra token"
            :src="getImageUrl('token_icons/aws_infra.png')"
            class="w-[6rem]"
          /> -->
          <TokenIcon
            title="aws infra token"
            logo-img-url="aws_infra.png"
            :has-shadow="true"
          />
          <img
            alt="active token"
            :src="getImageUrl('icons/active_token_badge.png')"
            class="absolute top-[4.5rem] left-[4rem] w-[1.5rem]"
          />
        </div>
      </div>
      <h2 class="text-xl mt-24">That's all folks!</h2>
    </div>
    <!-- <div class="flex flex-col items-center">
        <BaseButton
          v-if="!isLoading"
          class="mt-40"
        >
          Manage Token</BaseButton
        >
        <BaseButton
          v-if="!isLoading"
          class="mt-16"
          variant="secondary"
          @click="router.push('/')"
        >
          Generate new Canarytoken</BaseButton
        >
      </div>
    </div> -->
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
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import type { TokenDataType } from '@/utils/dataService';
import { requestTerraformSnippet } from '@/api/main.ts';
import StepState from '../StepState.vue';
import getImageUrl from '@/utils/getImageUrl';
import { TokenIcon } from '@/components/icons/TokenIcon.vue';

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  stepData: TokenDataType;
}>();

const router = useRouter();
const isLoading = ref(true);
const isError = ref(false);
const isSuccess = ref(false);
const errorMessage = ref('');

const terraformSnippet = ref('');

const { token, auth_token } = props.stepData;

onMounted(async () => {
  await handleRequestTerraformSnippet();
});

async function handleRequestTerraformSnippet() {
  const POLL_INTERVAL = 5000;

  isLoading.value = true;
  isError.value = false;
  isSuccess.value = false;

  try {
    const res = await requestTerraformSnippet({
      canarytoken: token,
      auth_token,
    });
    if (res.status !== 200) {
      isLoading.value = false;
      isError.value = true;
      errorMessage.value = res.data.message;
    }

    const handle = res.data.handle;

    const startTime = Date.now();
    const timeout = 5 * 60 * 1000; // 5 minutes

    const pollTerraformSnippet = async () => {
      try {
        const resWithHandle = await requestTerraformSnippet({ handle });

        if (resWithHandle.status !== 200) {
          isLoading.value = false;
          isError.value = true;
          errorMessage.value =
            resWithHandle.data.error ||
            'Error on requesting the Terraform Snippet';
          clearInterval(pollingTerraformSnippetInterval);
          return;
        }

        if (resWithHandle.data.message) {
          isLoading.value = false;
          isError.value = true;
          errorMessage.value = resWithHandle.data.message;
          clearInterval(pollingTerraformSnippetInterval);
          return;
        }

        // timeout
        if (Date.now() - startTime >= timeout) {
          isError.value = true;
          errorMessage.value = 'The operation took too long. Try again.';
          clearInterval(pollingTerraformSnippetInterval);
          return;
        }

        // success
        if (resWithHandle.data.terraform_module_snippet) {
          isLoading.value = false;
          isSuccess.value = true;

          const terraform_module_snippet =
            resWithHandle.data.terraform_module_snippet;

          console.log(terraform_module_snippet, 'terraform_module_snippet');

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
        isError.value = true;
        errorMessage.value =
          err.message || 'An error occurred while checking the Role. Try again';
        clearInterval(pollingTerraformSnippetInterval);
        return;
      } finally {
        isLoading.value = false;
      }
    };

    const pollingTerraformSnippetInterval = setInterval(
      pollTerraformSnippet,
      POLL_INTERVAL
    );
  } catch (err: any) {
    isError.value = true;
    errorMessage.value = err.message;
    isSuccess.value = false;
  }
}
</script>

<style scoped>
.wrap-code {
  :deep(pre) > code {
    white-space: pre-wrap;
    text-align: left;
  }
}
</style>
