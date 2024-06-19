<template>
  <div
    v-if="manageTokenResponse"
    class="flex flex-col items-center gap-8 mb-24"
  >
    <TokenIcon
      :title="tokenServices[getTokenType].label"
      :logo-img-url="tokenServices[getTokenType].icon"
      class="h-[4rem] w-[4rem]"
      :has-shadow="false"
    />
    <h2 class="text-xl text-center text-grey-800">
      {{ tokenServices[getTokenType].label }}
    </h2>
  </div>
  <div
    v-if="isLoading"
    class="flex flex-col items-center w-full gap-8"
  >
    <BaseSkeletonLoader
      type="circle"
      class="w-[60px] h-[60px]"
    />
    <BaseSkeletonLoader
      type="header"
      class="w-[200px]"
    />
    <BaseSkeletonLoader
      type="rectangle"
      class="md:max-w-[50vw] w-full h-[250px] mt-16"
    />
  </div>

  <BaseMessageBox
    v-if="error"
    variant="danger"
    message="Oh no! Something went wrong when managing your token data. Please refresh the page or try again later."
  >
  </BaseMessageBox>
  <div
    v-if="manageTokenResponse"
    class="md:mx-32 md:max-w-[50vw] w-full"
  >
    <div
      class="flex flex-col justify-center p-16 md:p-32 rounded-xl bg-grey-50 md:max-w-[50vw]"
    >
      <Suspense>
        <component
          :is="dynamicComponent"
          :token-backend-response="manageTokenResponse"
        />
        <template #fallback>
          <div class="flex flex-col w-full gap-8">
            <BaseSkeletonLoader
              class="w-[100px]"
              type="text"
            />
            <BaseSkeletonLoader
              class="w-full"
              type="header"
            />
          </div>
        </template>
      </Suspense>
      <MemoDisplay class="mt-32">{{
        manageTokenResponse.canarydrop.memo
      }}</MemoDisplay>
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
        <span v-if="!hasAlerts">This Token has never been triggered</span>
        <span v-else>
          This Token has been triggered
          <span class="font-bold">{{ hasAlerts }}</span>
          time{{ hasAlerts > 1 ? 's' : '' }}</span
        >
      </BaseMessageBox>
      <DeleteTokenButton
        :memo="manageTokenResponse.canarydrop.memo"
        :token="manageTokenResponse.canarydrop.canarytoken._value"
        :auth="manageTokenResponse.canarydrop.auth"
        :type="manageTokenResponse.canarydrop.type"
      />
    </div>
    <div class="flex justify-center sm:max-w-[50vw]">
      <BannerTextCanarytools class="mt-32 mb-8" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { manageToken } from '@/api/main.ts';
import SettingsToken from './SettingsToken.vue';
import { tokenServices } from '@/utils/tokenServices';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';
import { TOKENS_TYPE } from './constants';
import BannerTextCanarytools from '@/components/ui/BannerTextCanarytools.vue';
import DeleteTokenButton from '@/components/ui/DeleteTokenButton.vue';
import MemoDisplay from '@/components/ui/MemoDisplay.vue';
import TokenIcon from '@/components/icons/TokenIcon.vue';

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

/* AZURE CONFIG Exception handler */
/* CSS Cloned Site type can be an Azure ID Config token */
/* It checks if the token is an Azure ID Config token by verifying the expected_referrer value. */
/* If the expected_referrer is 'microsoftonline.com', it indicates that the token is an Azure ID Config token. */
const getTokenType = computed(() => {
  return manageTokenResponse.value.canarydrop.expected_referrer ===
    'microsoftonline.com'
    ? TOKENS_TYPE.AZURE_ENTRA_CONFIG
    : manageTokenResponse.value.canarydrop.type;
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

  try {
    const res = await manageToken(params);
    isLoading.value = false;
    manageTokenResponse.value = res.data as ManageTokenBackendType;
    tokenLogoUrl.value = `token_icons/${tokenServices[getTokenType.value].icon}`;
    hasAlerts.value =
      manageTokenResponse.value.canarydrop.triggered_details.hits.length;
    loadComponent();
  } catch (err: any) {
    console.log(err, 'err!');
    error.value = err.toString();
    router.push({ name: 'error' });
  } finally {
    isLoading.value = false;
  }
}

async function loadComponent() {
  dynamicComponent.value = await defineAsyncComponent(
    () => import(`@/components/tokens/${getTokenType.value}/ManageToken.vue`)
  );
}

loadComponent();

watch(() => route.params.token, fetchTokenData, { immediate: true });
</script>

<style></style>
