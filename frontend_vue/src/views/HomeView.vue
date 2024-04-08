<template>
  <AppLayoutGrid>
    <template
      v-for="(token, key) in tokenServices"
      :key="key"
    >
      <CardToken
        :title="token.label"
        :description="token.description"
        :logo-img-url="token.icon"
        :documentation-link="token.documentationLink"
        @click-token="() => handleClickToken(key as string)"
      />
    </template>
  </AppLayoutGrid>
</template>

<script setup lang="ts">
import AppLayoutGrid from '@/layout/AppLayoutGrid.vue';
import CardToken from '@/components/ui/CardToken.vue';
import { useModal } from 'vue-final-modal';
import ModalToken from '@/components/ModalToken.vue';
import { tokenServices } from '@/utils/tokenServices';

function handleClickToken(selectedToken: string) {
  const { open, close } = useModal({
    component: ModalToken,
    attrs: {
      selectedToken: selectedToken,
      closeModal: () => close(),
    },
  });
  open();
}
</script>
