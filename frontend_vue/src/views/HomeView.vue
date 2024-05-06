<template>
  <div class="my-24 text-center">
    <div>
      <h1 class="text-4xl font-semibold text-grey-900">
        Here goes something, like a
        <span class="text-green-500">clear</span> Headline.
      </h1>
      <h2 class="mt-8 font-md text-grey-400">
        Something else we want to tell users when they land here.
      </h2>
    </div>
    <h3 class="mt-32 text-xl text-grey-800">Generate Canarytoken</h3>
  </div>
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
