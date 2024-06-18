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
      <div>
        <BaseMessageBox
          v-if="errorMessage || successMessage"
          class="w-[90%] m-auto mb-16"
          :variant="successMessage ? 'success' : 'danger'"
          :message="errorMessage || successMessage"
        />
        <div class="w-full flex flex-row justify-center">
          <BaseButton variant="grey" class="mr-8" @click="modalOpen = false">No, keep it</BaseButton>
          <BaseButton variant="danger" :loading="isLoading" @click="deleteToken(token, auth)">Yes, delete</BaseButton>
        </div>
      </div>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
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
const router = useRouter();

const modalOpen = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const openDeleteModal = () => {
  modalOpen.value = true;
  errorMessage.value = '';
  successMessage.value = '';
  isLoading.value = false;
};

const deleteToken = async (token: string, auth: string) => {
  isLoading.value = true;
  const params = {
    auth: auth as string,
    token: token as string,
  };

  try {
    const res = await deleteTokenFnc(params);
    if (res.status === 200){
      successMessage.value = 'Yay! Your token, plus associated alerts, has been successfully deleted.'
      setTimeout(() => {
        modalOpen.value = false;
        router.push({ name: 'home' });
      }, 3000);
    }
    if (res.status === 403 || res.status === 500) errorMessage.value =  'Oh no! Something went wrong when deleting your token.';
    if (res.status === 404) router.push({ name: 'error' });
  } catch (err: any) {
    console.log(err, 'err!');
    errorMessage.value = err.toString();
  } finally {
    isLoading.value = false;
  }
}

</script>
