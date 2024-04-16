<template>
  <div
    v-if="manageTokenResponse"
    class="flex flex-col items-center gap-8 mb-24"
  >
    <img
      :src="getImageUrl(tokenLogoUrl)"
      class="h-[4rem]"
      aria-hidden="true"
      :alt="`${tokenServices[manageTokenResponse.canarydrop.type].label} logo`"
    />
    <h2 class="text-xl text-center text-grey-800">
      {{ tokenServices[manageTokenResponse.canarydrop.type].label }}
    </h2>
  </div>
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
  <div
    v-if="manageTokenResponse"
    class="flex flex-col justify-center p-16 md:p-32 md:mx-32 rounded-xl bg-grey-50 md:max-w-[50vw] w-full"
  >
    <component
      :is="dynamicComponent"
      :token-backend-response="manageTokenResponse"
    />
    <SettingsToken
      :token-backend-response="manageTokenResponse"
      class="mt-32"
    ></SettingsToken>
    <BaseMessageBox
      class="mt-32"
      :variant="hasAlerts ? 'danger' : 'info'"
      :text-link="hasAlerts ? 'Check History' : ''"
      @click="handleCheckHistory"
    >
      <!-- there should no risk of injection for unescaped html -->
      <!-- eslint-disable-next-line vue/no-v-html -->
      <span v-html="alertsMessage"></span>
    </BaseMessageBox>
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { manageToken } from '@/api/main.ts';
import SettingsToken from './SettingsToken.vue';
import { tokenServices } from '@/utils/tokenServices';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';
import getImageUrl from '@/utils/getImageUrl';

const route = useRoute();
const router = useRouter();

const isLoading = ref(false);
const error = ref(null);
const manageTokenResponse = ref();
const tokenLogoUrl = ref();

const dynamicComponent = ref({
  props: {},
});

const hasAlerts = ref(0);
const alertsMessage = computed(() => {
  return !hasAlerts.value
    ? 'This Token has never been triggered'
    : `This Token has been triggered <span class="font-bold">${hasAlerts.value}</span> time${hasAlerts.value > 1 ? 's' : ''}`;
});

function handleCheckHistory() {
  const auth = route.params.auth;
  const token = route.params.token;
  router.push({ name: 'history', params: { auth, token } });
}

async function fetchTokenData() {
  isLoading.value = true;

  const params = {
    auth: route.params.auth as string,
    token: route.params.token as string,
  };

  manageToken(params)
    .then((res) => {
      isLoading.value = false;
      manageTokenResponse.value = res.data as ManageTokenBackendType;
      tokenLogoUrl.value = `token_icons/${tokenServices[manageTokenResponse.value.canarydrop.type].icon}`;
      hasAlerts.value =
        manageTokenResponse.value.canarydrop.triggered_details.hits.length;

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
}

loadComponent();

watch(() => route.params.token, fetchTokenData, { immediate: true });
</script>

<style></style>