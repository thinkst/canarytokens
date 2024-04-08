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
  <div v-if="manageTokenResponse">
    <component
      :is="dynamicComponent"
      :tocken-backend-response="manageTokenResponse"
    />
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { manageToken } from '@/api/main.ts';

const route = useRoute();

const isLoading = ref(false);
const error = ref(null);
const manageTokenResponse = ref();

const dynamicComponent = ref({
  props: {},
});

async function fetchTokenData() {
  isLoading.value = true;

  const params = {
    auth: route.params.auth,
    token: route.params.token,
  };

  manageToken(params)
    .then((res) => {
      isLoading.value = false;
      manageTokenResponse.value = res.data;

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
        `@/components/tokens/${manageTokenResponse.value?.canarydrop.type}/ManageToken.vue`
      )
  );
  // dynamicComponent.value.props = {
  //   tockenBackendResponse: token,
  //   tokenSnippetData: tokenSnippetData.value,
  // };
}

loadComponent();

watch(() => route.params.token, fetchTokenData, { immediate: true });
</script>

<style></style>
