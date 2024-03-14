<template>
    <BaseModal :title="title" :hasBackButton="hasBackButton" @handleBackButton="handleBackButton">
        <template v-if="!isLoading">
            <ModalContentAddToken v-if="modalType === ModalType.AddToken" />
            <ModalContentNewToken v-if="modalType === ModalType.NewToken" />
            <ModalContentHowToUse v-else-if="modalType === ModalType.HowToUse" />
        </template>
        <p v-else>Loading</p>

        <!-- footer -->
        <template v-slot:footer v-if="!isLoading">
            <template v-if="modalType === ModalType.AddToken">
                <BaseButton variant="secondary" @click="handleAddToken">Create Token</BaseButton>
            </template>

            <template v-if="modalType === ModalType.NewToken">
                <BaseButton variant="secondary" @click="handleHowToUse">How to use</BaseButton>
                <BaseButton variant="secondary" @click="handleManageToken">Manage Token</BaseButton>
            </template>

            <template v-if="modalType === ModalType.HowToUse">
                <BaseButton variant="secondary" @click="handleManageToken">Manage Token</BaseButton>
            </template>
        </template>
    </BaseModal>

</template>

<script setup lang="ts">
import { ref,computed } from 'vue';
import ModalContentHowToUse from '@/components/ModalContentHowToUse.vue';
import ModalContentNewToken from './ModalContentNewToken.vue';
import ModalContentAddToken from './ModalContentAddToken.vue';

enum ModalType {
  AddToken = 'addToken',
  NewToken = 'newToken',
  HowToUse = 'howToUse',
}

const modalType = ref(ModalType.AddToken)
const isLoading = ref(false)

const title = computed(() => {
    switch (modalType.value) {
        case ModalType.AddToken:
            return 'Add Token'
        case ModalType.NewToken:
            return 'New Token'
        case ModalType.HowToUse:
            return 'How to use'
        default:
            return 'Add Token'
    }
})

const hasBackButton = computed(() => {
    return modalType.value === ModalType.HowToUse
})

function handleAddToken() {
    isLoading.value = true
    setTimeout(() => {
        isLoading.value = false
        modalType.value = ModalType.NewToken
    }, 1000)
}

function handleHowToUse() {
    modalType.value = ModalType.HowToUse
}

function handleManageToken() {
    console.log('manage token')
}

function handleBackButton() {
    modalType.value = ModalType.NewToken
}


</script>
