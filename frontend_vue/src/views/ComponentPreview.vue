<template>
  <div class="flex flex-col w-[200px] gap-16">
    <h1>Buttons</h1>
    <base-button>Primary</base-button>
    <base-button variant="secondary">Secondary</base-button>
    <base-button variant="text">Text!!</base-button>
  </div>
  <div class="flex flex-col w-[200px] gap-16">
    <h1>Modal</h1>
    <BaseButton @click="() => open()">Check modal</BaseButton>
  </div>
</template>

<script setup lang="ts">
// TODO: remove this view - for internal use only
import { useModal } from 'vue-final-modal'
import ModalAddToken from '@/components/ModalAddToken.vue';

  const { open } = useModal({
    component: ModalAddToken,
  })

</script>
