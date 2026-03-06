<template>
  <BaseModal
    :title="title"
    :has-close-button="hasCloseButton"
    @update:model-value="handleModalVisibilityChange"
  >
    <!-- Header -->
    <!-- Back Button-->
    <template #header-btn-left>
      <button
        v-if="hasBackButton"
        type="button"
        :aria-label="`Back`"
        class="w-24 h-24 text-sm duration-150 bg-transparent border border-solid rounded-full hover:text-white text-grey-300 border-grey-300 hover:bg-green-600 hover:border-green-300"
        @click="handleBackButton"
      >
        <font-awesome-icon
          icon="angle-left"
          aria-hidden="true"
        />
        <span class="fa-sr-only">Back</span>
      </button>
    </template>
    <!-- How to deploy ? Button-->
    <template #header-btn-right>
      <template v-if="!isLoading && modalType === ModalType.AddToken">
        <ButtonHowToDeploy
          :token-name="tokenServices[props.selectedToken].label"
          size="big"
          :is-open="showTooltip"
          @click="handleHowToUseButton"
        />
      </template>
    </template>
    <!-- Content -->
    <Suspense v-if="modalType === ModalType.AddToken">
      <ModalContentGenerateToken
        :selected-token="selectedToken"
        :trigger-submit="triggerSubmit"
        @token-generated="(formValues) => handleGenerateToken(formValues)"
        @invalid-submit="handleInvalidSubmit"
        @is-loading="isLoading = $event"
      />
      <template #fallback>
        <ModalContentGenerateTokenLoader />
      </template>
    </Suspense>
    <Suspense v-if="modalType === ModalType.NewToken">
      <ModalContentActivatedToken
        :new-token-response="newTokenResponse"
        :shoot-confetti="shootConfetti"
        @how-to-use="handleHowToUseButton"
      />
      <template #fallback>
        <ModalContentActivatedTokenLoader />
      </template>
    </Suspense>
    <ModalContentHowToUse
      v-else-if="modalType === ModalType.HowToUse"
      :selected-token="selectedToken"
    />
    <BaseMessageBox
      v-if="isSuspenseError || isGenerateTokenError"
      variant="danger"
      class="my-16"
      :message="
        errorMessage ||
        'Oh no! Something went wrong. Please refresh the page or try again later.'
      "
    >
    </BaseMessageBox>

    <!-- Footer -->
    <template #footer>
      <template v-if="isLoading">
        <BaseSkeletonLoader
          type="rectangle"
          class="w-[130px] h-[40px]"
        />
      </template>
      <template v-else>
        <template
          v-if="
            modalType === ModalType.AddToken &&
            !tokenServices[props.selectedToken].isCustomGenerateFlow
          "
        >
          <BaseButton
            variant="primary"
            :loading="isLoadngSubmit"
            @click.stop="handleAddTokenButton"
            >Create Canarytoken</BaseButton
          >
        </template>
        <template
          v-if="
            modalType === ModalType.AddToken &&
            tokenServices[props.selectedToken].isCustomGenerateFlow
          "
        >
          <BaseButton
            variant="primary"
            :loading="isLoadngSubmit"
            @click.stop="handleAddTokenButton"
            >Start creating Canarytoken</BaseButton
          >
        </template>

        <template v-if="modalType === ModalType.NewToken">
          <BaseButton
            variant="secondary"
            @click="handleHowToUseButton"
            >How to use</BaseButton
          >
          <BaseButton
            variant="secondary"
            @click="handleManageTokenButton"
            >Manage Canarytoken</BaseButton
          >
        </template>

        <template v-if="modalType === ModalType.HowToUse">
          <BaseButton
            variant="primary"
            @click="handleBackButton"
            >Got it!</BaseButton
          >
        </template>
      </template>
    </template>
    <!-- Banner ADV -->
    <template #banner>
      <BannerBirdCanarytools
        v-if="
          modalType === ModalType.NewToken || modalType === ModalType.HowToUse
        "
        class="mb-8"
      />
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, onErrorCaptured, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import type { BaseFormValuesType } from './tokens/types';
import ModalContentHowToUse from '@/components/ModalContentHowToUse.vue';
import ModalContentActivatedToken from './ModalContentActivatedToken.vue';
import ModalContentGenerateToken from './ModalContentGenerateToken.vue';
import ModalContentGenerateTokenLoader from '@/components/ui/ModalContentGenerateTokenLoader.vue';
import ModalContentActivatedTokenLoader from '@/components/ui/ModalContentActivatedTokenLoader.vue';
import BannerBirdCanarytools from '@/components/ui/BannerBirdCanarytools.vue';
import ButtonHowToDeploy from '@/components/ui/ButtonHowToDeploy.vue';
import { generateToken } from '@/api/main';
import { TOKENS_TYPE } from './constants';
import { tokenServices } from '@/utils/tokenServices';
import { addViewTransition } from '@/utils/utils';
import { setTokenData } from '@/utils/dataService.ts';
import type { TokenDataType } from '@/utils/dataService.ts';

enum ModalType {
  AddToken = 'addToken',
  NewToken = 'newToken',
  HowToUse = 'howToUse',
}

const props = defineProps<{
  selectedToken: string;
  closeModal: (options?: { keepRoute?: boolean }) => void | Promise<void>;
  selectedModalType?: string;
}>();

const router = useRouter();
const modalType = ref(props.selectedModalType || ModalType.AddToken);
const newTokenResponse = ref<{
  token_type: string;
  [key: string]: string | number;
}>({
  token_type: '',
});
const triggerSubmit = ref(false);
const isSuspenseError = ref(false);
const isGenerateTokenError = ref(false);
const errorMessage = ref('');
const isLoadngSubmit = ref(false);
const isLoading = ref(false);
const showTooltip = ref(false);
const shootConfetti = ref(false);
// Stack to keep track of loaded components
// Used for Modal navigation
const componentStack = ref<string[]>([]);

onMounted(() => {
  // Keep track of loaded components
  componentStack.value.push(modalType.value);
});

const title = computed(() => {
  switch (modalType.value) {
    case ModalType.AddToken:
      return `Create ${tokenServices[props.selectedToken].label} Token`;
    case ModalType.NewToken:
      return 'New Token Created!';
    case ModalType.HowToUse:
      return 'How does this work?';
    default:
      return 'Add Token';
  }
});

const hasBackButton = computed(() => {
  return (
    modalType.value === ModalType.AddToken ||
    modalType.value === ModalType.HowToUse
  );
});

const hasCloseButton = computed(() => {
  return modalType.value === ModalType.NewToken;
});

/* AZURE CONFIG Exception handler */
/* Azure ID Config must submit a POST request as CSS Cloned Site */
const getTokenType = computed(() => {
  return props.selectedToken === TOKENS_TYPE.AZURE_ENTRA_CONFIG
    ? TOKENS_TYPE.CSS_CLONED_SITE
    : props.selectedToken;
});

function handleAddTokenButton() {
  // triggerSubmit inside ModalContentGenerateToken
  triggerSubmit.value = true;
}

async function handleHowToUseButton() {
  await addViewTransition(
    () => (modalType.value = ModalType.HowToUse)
    // Keep track of loaded components
  ).then(() => componentStack.value.push(modalType.value));
}

async function handleManageTokenButton() {
  const auth = newTokenResponse.value?.auth_token;
  const token = newTokenResponse.value?.token;
  await router.push({ name: 'manage', params: { auth, token } });
  await props.closeModal({ keepRoute: true });
}

async function handleBackButton() {
  componentStack.value.pop();
  // If the stack is empty, close the modal
  if (componentStack.value.length === 0) {
    props.closeModal();
  } else {
    // Otherwise, show the top component from the stack
    await addViewTransition(
      () =>
        (modalType.value =
          componentStack.value[componentStack.value.length - 1])
    );
  }
}

async function handleGenerateToken(formValues: BaseFormValuesType) {
  try {
    isLoadngSubmit.value = true;
    const res = await generateToken({
      ...formValues,
      token_type: getTokenType.value,
    });
    if (res.status !== 200) {
      isLoadngSubmit.value = false;
      triggerSubmit.value = false;
      errorMessage.value = res.data.error_message;
      return (isGenerateTokenError.value = true);
    }
    /* AZURE CONFIG Exception handler */
    /* Overwrite backend response for Azure ID Config token type */
    /* It's needed as Azure ID Config returns CSS Cloned Site */
    newTokenResponse.value = {
      ...res.data,
      token_type: props.selectedToken,
    };

    // remove errors & loading
    isGenerateTokenError.value = false;
    errorMessage.value = '';
    isLoadngSubmit.value = false;
    triggerSubmit.value = false;

    // if Token type has Custom Generate flow, go to custom page
    if (tokenServices[props.selectedToken].isCustomGenerateFlow) {
      setTokenData(res.data as TokenDataType);
      await router.push({
        name: 'generate-custom',
        params: {
          tokentype: props.selectedToken,
        },
      });
      await props.closeModal({ keepRoute: true });
      return;
    }

    await addViewTransition(
      () => (modalType.value = ModalType.NewToken)
      // Keep track of loaded components
    ).then(() => componentStack.value.push(modalType.value));
  } catch (err: any) {
    triggerSubmit.value = false;
    isGenerateTokenError.value = true;
    if (err.response.data.error_message) {
      errorMessage.value = err.response.data.error_message;
    }
  } finally {
    triggerSubmit.value = false;
  }
}

function handleInvalidSubmit() {
  triggerSubmit.value = false;
}

function handleModalVisibilityChange(isOpen: boolean) {
  if (!isOpen) {
    props.closeModal();
  }
}

// More info on Error handling for Suspense:
// https://vuejs.org/guide/built-ins/suspense.html#error-handling
onErrorCaptured((err) => {
  console.error('Error loading component:', err.toString());
  isSuspenseError.value = true;
  return true;
});

// To cleanup the UI
// Reset error on modal type change
watch(
  modalType,
  () => {
    isSuspenseError.value = false;
  },
  { deep: true }
);

// Show tooltip 'How does it work' for 2 seconds on loaded modal
watch(isLoading, () => {
  if (isLoading.value === false) {
    showTooltip.value = true;
    setTimeout(() => {
      showTooltip.value = false;
    }, 2000);
  }
});
// Only shoot confetti after generating a new token
watch(modalType, (newVal, oldVal) => {
  if (oldVal === ModalType.AddToken && newVal === ModalType.NewToken) {
    shootConfetti.value = true;
  } else {
    shootConfetti.value = false;
  }
});
</script>
