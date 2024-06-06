<template>
  <div class="m-auto mt-32">
    <base-button variant="danger" @click="openDeleteModal">Delete this token</base-button>
  </div>
  <BaseModal
    v-model="modalOpen"
    documentation-link=""
    :has-back-button="false"
    :title="`Delete token with memo: '${memo}'`">
    <p class="text-center">
      This token has been triggered <span class="bg-grey-300 rounded-full py-[2px] px-8">{{
      alertsCount }}</span> times. Are you sure you want to delete?</p>
    <template #footer>
      <div class="w-full flex flex-row justify-end pr-[3rem]">
        <span v-if="errorMessage">{{ errorMessage }}</span>
        <BaseButton class="secondary mr-8" @click="modalOpen = false">No</BaseButton>
        <BaseButton class="danger" :loading="isLoading" @click="deleteToken(token, auth)">Yes</BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { deleteToken as deleteTokenFnc } from '@/api/main';

defineProps<{
  alertsCount: string | number;
  memo: string;
  token: string;
  auth: string
}>();

const modalOpen = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

const openDeleteModal = () => modalOpen.value = true;

const deleteToken = async (token: string, auth: string) => {
  isLoading.value = true;
  const params = {
    auth: auth as string,
    token: token as string,
  };

  try {
    const res = await deleteTokenFnc(params);
    console.log(res)
    isLoading.value = false
    if (res.status === 404) modalOpen.value = false
  } catch (err: any) {
    console.log(err, 'err!');
    errorMessage.value = err.toString();
  } finally {
    isLoading.value = false;
    modalOpen.value = false
  }
}

</script>
