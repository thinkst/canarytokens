<template>
  <div class="flex flex-row items-center justify-between mt-32">
    <div class="flex flex-col">
      <span>Delete token</span>
      <span class="text-xs leading-4 text-grey-500 pr-[3rem]"
        >Remove this token and delete all related alerts</span
      >
    </div>
    <div>
      <base-button
        variant="danger"
        :border="true"
        @click="openDeleteModal(type, auth, token)"
        >Delete</base-button
      >
    </div>
  </div>
</template>

<script setup lang="ts">
import { useModal } from 'vue-final-modal';
import DeleteTokenModal from '@/components/ui/DeleteTokenModal.vue';

defineProps<{
  memo: string;
  token: string;
  auth: string;
  type: string;
}>();

function openDeleteModal(type: string, auth: string, token: string) {
  const { open, close } = useModal({
    component: DeleteTokenModal,
    attrs: {
      type,
      auth,
      token,
      closeModal: () => close(),
    },
  });
  open();
}
</script>
