<template>
  <AppLayoutGrid>
    <!-- <CardToken
      title="Very long long title"
      description="Alert when a Kubeconfig Token is used"
      documentation-link="#"
      @click-token="() => open()"
    />
    <CardToken
      title="Very short"
      description="A description for a token, it’s very long and goes on three lines!"
      logo-img-url="s3_bucket.png"
      documentation-link="#"
      @click-token="() => open()"
    />
    <CardToken
      title="Very loooon title that might go 3 lines"
      description="Another description for this token"
      logo-img-url="s3_bucket.png"
      documentation-link="#"
      @click-token="() => open()"
    />
    <CardToken
      title="Very short"
      description="Another description for this token"
      logo-img-url="s3_bucket.png"
      documentation-link="#"
      @click-token="() => open()"
    /> -->
    <template
      v-for="(token, key) in tokensOperations"
      :key="key"
    >
      <CardToken
        :title="token.label"
        :description="token.description"
        :logo-img-url="token.icon"
        :documentation-link="token.documentationLink"
        @click-token="() => handleClickToken(key)"
      />
    </template>
  </AppLayoutGrid>
</template>

<script setup lang="ts">
import AppLayoutGrid from '@/layout/AppLayoutGrid.vue';
import CardToken from '@/components/CardToken.vue';
import { useModal } from 'vue-final-modal';
import { useTokens } from '@/composables/useTokens';
import ModalAddToken from '@/components/ModalAddToken.vue';

// const { open } = useModal({
//   component: ModalAddToken,
//   attrs: {},
// });

function handleClickToken(selectedToken: string) {
  const { open } = useModal({
    component: ModalAddToken,
    attrs: {
      selectedToken: selectedToken,
    },
  });
  open();
}

const { tokensOperations } = useTokens();
// console.log(tokensOperations, 'tokensOperations');
</script>
