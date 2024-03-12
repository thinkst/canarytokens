<template>
  <AppLayoutGrid>
    <div>Home</div>
    <button @click="() => open()">Check modal</button>
  </AppLayoutGrid>
</template>

<script setup lang="ts">
import AppLayoutGrid from '@/layout/AppLayoutGrid.vue';
import { useModal } from 'vue-final-modal'
import BaseModal from '@/components/base/_BaseModal.vue'

  const { open, close } = useModal({
    component: BaseModal,
    attrs: {
      title: 'My lovely modal',
      onConfirm() {
        close()
      },
    },
    slots: {
      default: 'Test modal content Test modal content Test modal content',
      footer: `<button @click="onConfirm" class="btn btn-green">Footer content</button>`,
    },
  })



</script>
