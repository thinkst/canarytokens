<template>
  <BaseModal
    :title="title"
    :has-back-button="hasBackButton"
    @handle-back-button="handleBackButton"
  >
    <template v-if="!isLoading">
      <ModalContentAddToken
        v-if="modalType === ModalType.AddToken"
        :selected-token="selectedToken"
      />
      <ModalContentNewToken
        v-if="modalType === ModalType.NewToken"
        :new-token-data="creationResponse"
      />
      <ModalContentHowToUse v-else-if="modalType === ModalType.HowToUse" />
    </template>
    <p v-else>Loading</p>

    <!-- footer -->
    <template
      v-if="!isLoading"
      #footer
    >
      <template v-if="modalType === ModalType.AddToken">
        <BaseButton
          variant="secondary"
          @click="handleAddToken"
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
          @click="handleManageToken"
          >Manage Token</BaseButton
        >
      </template>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import ModalContentHowToUse from '@/components/ModalContentHowToUse.vue';
import ModalContentNewToken from './ModalContentNewToken.vue';
import ModalContentAddToken from './ModalContentAddToken.vue';
import { generateToken } from '@/api/main';
import { store } from '@/store/store.ts';

enum ModalType {
  AddToken = 'addToken',
  NewToken = 'newToken',
  HowToUse = 'howToUse',
}

const modalType = ref(ModalType.AddToken);
const isLoading = ref(false);
const creationResponse = ref({});

defineProps<{
  selectedToken: string;
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
  isLoading.value = true;
  generateToken({
    email: 'user@example.com',
    webhook_url: 'http://example.com',
    memo: 'string',
    token_type: 'cc',
  })
    .then((res) => {
      console.log(res, 'res');
      creationResponse.value = res.data;
    })
    .catch((err) => {
      console.log(err, err);
    })
    .finally(() => {
      isLoading.value = false;
      modalType.value = ModalType.NewToken;
      store.newTokenData = {};
    });
  // setTimeout(() => {
  //   isLoading.value = false;
  //   modalType.value = ModalType.NewToken;
  // }, 1000);
  // console.log('submit:', store.newTokenData);

  // reset form
  store.newTokenData = {};
}

function handleHowToUse() {
  modalType.value = ModalType.HowToUse;
}

function handleManageToken() {
  console.log('manage token');
}

function handleBackButton() {
  modalType.value = ModalType.NewToken;
}
</script>
