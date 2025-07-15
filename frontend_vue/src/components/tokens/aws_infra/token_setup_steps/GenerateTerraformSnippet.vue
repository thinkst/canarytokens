<template>
  <section class="section-terraform-snippet flex flex-col items-center">
    <div class="infra-token__title-wrapper text-center">
      <h2>
        {{
          isLoading || isError
            ? 'Preparing the Terraform module...'
            : 'Deploy your decoys'
        }}
      </h2>
    </div>
    <StepState
      v-if="isLoading || isError"
      :is-loading="isLoading"
      :is-error="isError"
      :error-message="errorMessage"
    >
      <template #loading>
        <GenerateTerraformSnippetLoadingState />
      </template>
    </StepState>
    <div
      v-if="isSuccess"
      class="flex flex-col items-center"
    >
      <div class="text-left max-w-[100%]">
        <div>
          <BaseMessageBox
            class="mb-24 sm:w-[100%] md:max-w-[60vw] lg:max-w-[50vw] xl:max-w-[40vw]"
            variant="success"
            >Your decoy infrastructure design has been generated and stored. All
            that remains is to include it into your Terraform configuration, and
            apply it.</BaseMessageBox
          >
        </div>
        <BaseCard
          class="p-40 flex items-center flex-col text-left sm:max-w-[100%] md:max-w-[60vw] lg:max-w-[50vw] xl:max-w-[40vw] place-self-center"
        >
          <div class="text-center mb-16 flex flex-col items-center">
            <img
              :src="getImageUrl('terraform_icon.svg')"
              alt="terraform-icon"
              class="w-[2.5rem] h-[2.5rem] mb-8"
            />
            <h2 class="textmd mb-16">
              Add this snippet to your Terraform configuration file then run<br />
              <span class="monospace">$ terraform init</span> to import the
              module, and <span class="monospace">$terraform apply</span> to
              create the resources.
            </h2>
          </div>
          <BaseLabelArrow
            id="terraform-module"
            label="Copy Terraform snippet"
            arrow-word-position="last"
            arrow-variant="one"
            class="z-10 text-right"
          />
          <BaseCodeSnippet
            id="terraform-module"
            lang="bash"
            :code="terraformSnippet"
            class="w-full wrap-code"
            custom-height="100px"
          ></BaseCodeSnippet>
          <div
            class="text-left sm:text-center flex mt-24 gap-8 items-center justify-center"
          >
            <p>How do I use this module?</p>
            <button
              v-tooltip="{
                content: 'Check details',
                triggers: ['hover'],
              }"
              class="w-24 h-24 text-sm duration-150 bg-transparent border border-solid rounded-full hover:text-white hover:bg-green-600 hover:border-green-300 shrink-0"
              aria-label="What's this snippet doing?"
              @click="handleShowModalInfoModule"
            >
              <font-awesome-icon
                icon="question"
                aria-hidden="true"
              />
            </button>
          </div>
          <div
            class="text-left sm:text-center flex mt-8 gap-8 items-center justify-center"
          >
            <p>How do I clean up IAM resources for Canarytokens Inventory?</p>
            <button
              v-tooltip="{
                content: 'Check details',
                triggers: ['hover'],
              }"
              class="w-24 h-24 text-sm duration-150 bg-transparent border border-solid rounded-full hover:text-white hover:bg-green-600 hover:border-green-300 shrink-0"
              aria-label="How do I cleanup my AWS accont?"
              @click="handleShowModalCleanup"
            >
              <font-awesome-icon
                icon="question"
                aria-hidden="true"
              />
            </button>
          </div>
        </BaseCard>
      </div>

      <h2 class="text-md mt-24 text-center">
        That’s it! Once you’ve applied the Terraform configuration <br />and
        created the decoy resources, any interactions with them will give you an
        alert.
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
import { ref, onMounted, watch, defineAsyncComponent } from 'vue';
import { useRouter } from 'vue-router';
import getImageUrl from '@/utils/getImageUrl';
import type { TokenDataType } from '@/utils/dataService';
import { TOKENS_TYPE } from '@/components/constants.ts';
import { requestTerraformSnippet } from '@/api/awsInfra.ts';
import { launchConfetti } from '@/utils/confettiEffect';
import StepState from '@/components/tokens/aws_infra/StepState.vue';
import { useModal } from 'vue-final-modal';
import {
  StepStateEnum,
  useStepState,
} from '@/components/tokens/aws_infra/useStepState.ts';
import GenerateTerraformSnippetLoadingState from '@/components/tokens/aws_infra/token_setup_steps/GenerateTerraformSnippetLoadingState.vue';

const ModalInfoTerraformModule = defineAsyncComponent(
  () =>
    import(
      '@/components/tokens/aws_infra/token_setup_steps/ModalInfoTerraformSnippet.vue'
    )
);

const ModalInfoCleanup = defineAsyncComponent(
  () =>
    import(
      '@/components/tokens/aws_infra/token_setup_steps/ModalInfoCleanup.vue'
    )
);

const emits = defineEmits(['updateStep', 'storeCurrentStepData']);

const props = defineProps<{
  initialStepData: TokenDataType;
}>();

const router = useRouter();
const stateStatus = ref<StepStateEnum>(StepStateEnum.LOADING);
const { isLoading, isError, isSuccess } = useStepState(stateStatus);
const errorMessage = ref('');

const terraformSnippet = ref('');
const cleaupSnippet = ref('');

const { token, auth_token } = props.initialStepData;

onMounted(async () => {
  await handleRequestTerraformSnippet();
  window.scrollTo({
    top: 0,
    behavior: 'smooth',
  });
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
            resWithHandle.data.message ||
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

          const source = resWithHandle.data.terraform_module_snippet.source;
          const module = resWithHandle.data.terraform_module_snippet.module;

          terraformSnippet.value = generateTerraformSnippet(
            source,
            module
          );

          const roleName = resWithHandle.data.role_cleanup_commands.role_name;
          const customerAwsAccount =
            resWithHandle.data.role_cleanup_commands.customer_aws_account;

          cleaupSnippet.value = generateCleanupSnippet(
            roleName,
            customerAwsAccount
          );

          emits('storeCurrentStepData', {
            token,
            auth_token,
            terraformSnippet: terraformSnippet.value,
            cleaupSnippet: cleaupSnippet.value,
          });
          clearInterval(pollingTerraformSnippetInterval);
          return;
        }
      } catch (err: any) {
        stateStatus.value = StepStateEnum.ERROR;
        errorMessage.value = err.response?.data?.message ||
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
    errorMessage.value = err.response?.data?.message || err.message;
  }
}

function handleManageTokenButton() {
  router.push({ name: 'manage', params: { auth: auth_token, token } });
}

function handleShowModalInfoModule() {
  const { open, close } = useModal({
    component: ModalInfoTerraformModule,
    attrs: {
      closeModal: () => close(),
    },
  });
  open();
}

function generateTerraformSnippet(source: string, module: string) {
  return `module "${module}" {
  source = "${source}" }`
}

function generateCleanupSnippet(customerAwsAccount: string, roleName: string) {
  return `aws iam detach-role-policy --role-name ${roleName} --policy-arn arn:aws:iam::${customerAwsAccount}:policy/Canarytokens-Inventory-ReadOnly-Policy

aws iam delete-policy --policy-arn arn:aws:iam::${customerAwsAccount}:policy/Canarytokens-Inventory-ReadOnly-Policy

aws iam delete-role --role-name  ${roleName}`;
}

function handleShowModalCleanup() {
  const { open, close } = useModal({
    component: ModalInfoCleanup,
    attrs: {
      closeModal: () => close(),
      cleanupSnippetCommands: cleaupSnippet.value
    },
  });
  open();
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
    word-break: break-word;
  }
}

.monospace {
  font-family: 'Courier New', Courier, monospace;
}
</style>
