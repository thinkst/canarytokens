<template>
  <div
    v-if="isLoading"
    class="loading"
  >
    Loading...
  </div>

  <div
    v-if="error"
    class="error"
  >
    {{ error }}
  </div>
  <div v-if="token">
    <component
      :is="dynamicComponent"
      :tocken-backend-response="token"
      :token-snippet-data="tokenSnippetData"
    />
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { manageToken } from '@/api/main.ts';
import type { ManageTokenType } from '@/components/types.ts';
import { useTokens } from '@/composables/useTokens';

const route = useRoute();
const { tokensOperations } = useTokens();

const isLoading = ref(false);
const error = ref(null);
const token = ref<ManageTokenType>();

const dynamicComponent = ref({
  props: {},
});
const tokenSnippetData = ref();

async function fetchTokenData() {
  isLoading.value = true;

  const params = {
    auth: route.params.auth,
    token: route.params.token,
  };

  manageToken(params)
    .then((res) => {
      isLoading.value = false;
      token.value = res.data;
      const tokenType = token.value?.canarydrop.type;

      if (
        tokenType !== undefined &&
        tokensOperations.value[tokenType]?.getManageTokenData
      ) {
        tokenSnippetData.value = tokensOperations.value[
          tokenType
        ].getManageTokenData(token.value);
      }

      loadComponent();
    })
    .catch((err) => {
      console.log(err, 'err!');
      error.value = err.toString();
    })
    .finally(() => {
      isLoading.value = false;
    });
}

async function loadComponent() {
  dynamicComponent.value = await defineAsyncComponent(
    () =>
      import(
        `@/components/tokens/${token.value?.canarydrop.type}/ManageToken.vue`
      )
  );
  dynamicComponent.value.props = {
    tockenBackendResponse: token,
    tokenSnippetData: tokenSnippetData.value,
  };
}

loadComponent();

watch(() => route.params.token, fetchTokenData, { immediate: true });
</script>

<style></style>
