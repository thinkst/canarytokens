<template>
  <BaseModal
    :title="title"
    :has-back-button="hasBackButton"
    @handle-back-button="handleBackButton"
  >
    <Suspense v-if="modalType === ModalType.AddToken">
      <ModalContentGenerateToken
        :selected-token="selectedToken"
        :trigger-submit="triggerSubmit"
        @token-generated="(formValues) => handleGenerateToken(formValues)"
        @invalid-submit="handleInvalidSubmit"
      />
      <template #fallback>
        <ModalContentGenerateTokenLoader />
      </template>
    </Suspense>
    <Suspense v-if="modalType === ModalType.NewToken">
      <ModalContentActivatedToken :new-token-response="newTokenResponse" />
      <template #fallback>
        <ModalContentActivatedTokenLoader />
      </template>
    </Suspense>
    <ModalContentHowToUse
      v-else-if="modalType === ModalType.HowToUse"
      :selected-token="selectedToken"
    />
    <BaseMessageBox
      v-if="isSuspenseError"
      variant="danger"
      message="Oh no! Something went wrong. Please refresh the page or try again later."
    >
    </BaseMessageBox>

    <!-- footer -->
    <template #footer>
      <template v-if="modalType === ModalType.AddToken">
        <BaseButton
          variant="primary"
          @click.stop="handleAddToken"
          >Create Token</BaseButton
        >
      </template>

      <template v-if="modalType === ModalType.NewToken">
        <BaseButton
          variant="secondary"
          @click="handleHowToUse"
          >How to use</BaseButton
        >
        <BaseButton
          variant="secondary"
          @click="handleManageToken"
          >Manage Token</BaseButton
        >
      </template>

      <template v-if="modalType === ModalType.HowToUse">
        <BaseButton
          variant="secondary"
          @click="handleManageToken()"
          >Manage Token</BaseButton
        >
      </template>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, onErrorCaptured, watch } from 'vue';
import { useRouter } from 'vue-router';
import type { BaseFormValuesType } from './tokens/types';
import ModalContentHowToUse from '@/components/ModalContentHowToUse.vue';
import ModalContentActivatedToken from './ModalContentActivatedToken.vue';
import ModalContentGenerateToken from './ModalContentGenerateToken.vue';
import ModalContentGenerateTokenLoader from '@/components/ui/ModalContentGenerateTokenLoader.vue';
import ModalContentActivatedTokenLoader from '@/components/ui/ModalContentActivatedTokenLoader.vue';
import { generateToken } from '@/api/main';
import { TOKENS_TYPE } from './constants';

enum ModalType {
  AddToken = 'addToken',
  NewToken = 'newToken',
  HowToUse = 'howToUse',
}
const router = useRouter();
const modalType = ref(ModalType.AddToken);
const newTokenResponse = ref<{
  token_type: string;
  [key: string]: string | number;
}>({
  token_type: '',
});
const triggerSubmit = ref(false);
const isSuspenseError = ref(false);

const props = defineProps<{
  selectedToken: string;
  closeModal: () => void;
}>();

const title = computed(() => {
  switch (modalType.value) {
    case ModalType.AddToken:
      return 'Add Token';
    case ModalType.NewToken:
      return 'New Token';
    case ModalType.HowToUse:
      return 'How to use';
    default:
      return 'Add Token';
  }
});

const hasBackButton = computed(() => {
  return modalType.value === ModalType.HowToUse;
});

/* AZURE CONFIG Exception handler */
/* Azure ID Config must submit a POST request as CSS Cloned Site */
const getTokenType = computed(() => {
  return props.selectedToken === TOKENS_TYPE.AZURE_ENTRA_CONFIG
    ? TOKENS_TYPE.CSS_CLONED_SITE
    : props.selectedToken;
});

function handleAddToken() {
  // triggerSubmit inside ModalContentGenerateToken
  triggerSubmit.value = true;
}

async function handleGenerateToken(formValues: BaseFormValuesType) {
  try {
    const res = await generateToken({
      ...formValues,
      token_type: getTokenType.value,
    });
    /* AZURE CONFIG Exception handler */
    /* Overwrite backend response for Azure ID Config token type */
    /* It's needed as Azure ID Config returns CSS Cloned Site */
    newTokenResponse.value = {
      ...res.data,
      token_type: props.selectedToken,
    };
  } catch (err) {
    triggerSubmit.value = false;
    console.log(err, 'err');
  } finally {
    triggerSubmit.value = false;
    modalType.value = ModalType.NewToken;
  }
}

function handleInvalidSubmit() {
  triggerSubmit.value = false;
}

function handleHowToUse() {
  modalType.value = ModalType.HowToUse;
}

function handleManageToken() {
  const auth = newTokenResponse.value?.auth_token;
  const token = newTokenResponse.value?.token;
  router.push({ name: 'manage', params: { auth, token } });
  props.closeModal();
}

function handleBackButton() {
  modalType.value = ModalType.NewToken;
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
watch(modalType.value, () => {
  isSuspenseError.value = false;
});
</script>
