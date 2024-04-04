<template>
  <BaseModal
    :title="title"
    :has-back-button="hasBackButton"
    @handle-back-button="handleBackButton"
  >
    <template v-if="!isLoading">
      <ModalContentGenerateToken
        v-if="modalType === ModalType.AddToken"
        :selected-token="selectedToken"
        :trigger-submit="triggerSubmit"
        @token-generated="(formValues) => handleGenerateToken(formValues)"
        @invalid-submit="handleInvalidSubmit"
      />
      <ModalContentActivatedToken
        v-if="modalType === ModalType.NewToken"
        :new-token-response="newTokenResponse"
      />
      <ModalContentHowToUse
        v-else-if="modalType === ModalType.HowToUse"
        :selected-token="selectedToken"
      />
    </template>
    <p v-else>Loading</p>

    <!-- footer -->
    <template
      v-if="!isLoading"
      #footer
    >
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
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import type { BaseFormValuesType } from './tokens/types';
import ModalContentHowToUse from '@/components/ModalContentHowToUse.vue';
import ModalContentActivatedToken from './ModalContentActivatedToken.vue';
import ModalContentGenerateToken from './ModalContentGenerateToken.vue';
import { generateToken } from '@/api/main';

enum ModalType {
  AddToken = 'addToken',
  NewToken = 'newToken',
  HowToUse = 'howToUse',
}
const router = useRouter();
const modalType = ref(ModalType.AddToken);
const isLoading = ref(false);
const newTokenResponse = ref<{
  token_type: string;
  [key: string]: string | number;
}>({
  token_type: '',
});
const triggerSubmit = ref(false);

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

function handleAddToken() {
  // triggerSubmit inside ModalContentGenerateToken
  triggerSubmit.value = true;
}

function handleGenerateToken(formValues: BaseFormValuesType) {
  isLoading.value = true;
  generateToken({ ...formValues, token_type: props.selectedToken })
    .then((res) => {
      isLoading.value = false;
      newTokenResponse.value = res.data;
    })
    .catch((err) => {
      isLoading.value = false;
      triggerSubmit.value = false;
      console.log(err, 'err');
    })
    .finally(() => {
      isLoading.value = false;
      triggerSubmit.value = false;
      modalType.value = ModalType.NewToken;
    });
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
  modalType.value = ModalType.NewToken;
}
</script>