<template>
  <AppLayoutGrid>
    <div>Home</div>
    <button @click="() => open()">Check modal</button>
  </AppLayoutGrid>
</template>

<script setup lang="ts">
import AppLayoutGrid from '@/layout/AppLayoutGrid.vue';
import { useModal } from 'vue-final-modal'
import ModalAddToken from '@/components/ModalAddToken.vue';

  const { open, close } = useModal({
    component: ModalAddToken,
    // attrs: {
    //   onConfirm() {
    //     close()
    //   },
    // },
  })



</script>
