<template>
    <BaseModal :title="title" :hasBackButton="hasBackButton">
        <template v-if="!isLoading">
            <ModalContentAddToken v-if="modalType === ModalType.AddToken" />
            <ModalContentNewToken v-if="modalType === ModalType.NewToken" />
            <ModalContentHowToUse v-else-if="modalType === ModalType.HowToUse" />
        </template>
        <p v-else>Loading</p>

        <!-- footer -->
        <div class="modal-footer" v-if="modalType === ModalType.AddToken">
            <button @click="handleAddToken">Add</button>
        </div>

        <div class="modal-footer" v-if="modalType === ModalType.NewToken">
            <button @click="handleHowToUse">How to use</button>
            <button @click="handleManageToken">Manage Token</button>
        </div>

        <div class="modal-footer" v-if="modalType === ModalType.HowToUse">
            <button @click="handleManageToken">Manage Token</button>
        </div>
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


</script>
