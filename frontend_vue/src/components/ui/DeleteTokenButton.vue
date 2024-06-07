<template>
  <div class="flex flex-row justify-between items-center mt-32">
    <div class="flex flex-col">
      <span>Delete token</span>
      <span class="text-xs leading-4 text-grey-500 pr-[3rem]">Remove this token and delete all related alerts</span>
    </div>
    <div> <base-button variant="danger" @click="openDeleteModal">Delete</base-button></div>
  </div>
  <BaseModal
    v-model="modalOpen"
    documentation-link=""
    :has-back-button="false"
    :title="`Delete token`">
    <span class="relative mb-16">
      <img
      :src="getImageUrl(`token_icons/${tokenServices[type].icon}`)"
      :alt="`${tokenServices[type].label}`"
      class="w-[6rem]">
      <img
      :src="getImageUrl(`token_icons/delete_token_badge.png`)"
      :alt="`${tokenServices[type].label}`"
      class="absolute w-[1.3rem] bottom-[.5rem] right-[.3rem]" />
    </span>
    <div class="text-center">
      <p class="text-xl font-semibold leading-normal text-grey-800">Are you sure you want to delete this token?</p>
      <p class="text-normal leading-normal text-grey-300 mt-8">All associated alerts will be permanently lost</p>
    </div>
    <template #footer>
      <div class="w-full flex flex-row justify-center">
        <span v-if="errorMessage">{{ errorMessage }}</span>
        <BaseButton variant="grey" class="mr-8" @click="modalOpen = false">No, keep it</BaseButton>
        <BaseButton variant="danger" :loading="isLoading" @click="deleteToken(token, auth)">Yes, delete</BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { deleteToken as deleteTokenFnc } from '@/api/main';
import { tokenServices } from '@/utils/tokenServices';
import getImageUrl from '@/utils/getImageUrl';

defineProps<{
  alertsCount: string | number;
  memo: string;
  token: string;
  auth: string;
  type: string;
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
    if (res) modalOpen.value = false
  } catch (err: any) {
    console.log(err, 'err!');
    errorMessage.value = err.toString();
  } finally {
    isLoading.value = false;
    modalOpen.value = false
  }
}

</script>
