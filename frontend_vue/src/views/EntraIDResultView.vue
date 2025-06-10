<template>
  <AppLayoutOneColumn>
    <div class="flex flex-col items-center gap-8 mb-24">
      <img
        :src="getImageUrl(logoURL)"
        class="h-[4rem]"
        aria-hidden="true"
        :alt="` Azure Entra ID login logo`"
      />
      <h2 class="text-xl text-center text-grey-800">
        Automatic Setup Process Complete
      </h2>
    </div>
    <div
      class="flex flex-col justify-center p-16 md:p-32 md:mx-32 rounded-xl bg-grey-50 md:max-w-[50vw] w-full"
    >
      <BaseMessageBox
        class="mb-16"
        :message="alertsMessage"
        :variant="variant"
      />
      <BaseButton
        class="m-auto"
        variant="secondary"
        @click="closeWindow()"
        >Close Window</BaseButton
      >
      <BannerDeviceCanarytools class="my-8" />
    </div>
  </AppLayoutOneColumn>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import AppLayoutOneColumn from '@/layout/AppLayoutOneColumn.vue';
import BannerDeviceCanarytools from '@/components/ui/BannerDeviceCanarytools.vue';
import {
  ENTRA_ID_FEEDBACK_TYPES,
  ENTRA_ID_FEEDBACK_MESSAGES,
} from '@/components/constants';
import getImageUrl from '@/utils/getImageUrl';

const route = useRoute();
const router = useRouter();
const logoURL = ref('token_icons/azure_id_config.png');

onMounted(async () => {
  if (
    !Object.values(ENTRA_ID_FEEDBACK_TYPES).includes(
      route.params.result as string
    )
  )
    router.push({ name: 'error' });
});

const alertsMessage = computed(() => {
  if (
    route.params.result ===
    ENTRA_ID_FEEDBACK_TYPES.ENTRA_STATUS_HAS_CUSTOM_CSS_ALREADY
  )
    return ENTRA_ID_FEEDBACK_MESSAGES.ENTRA_STATUS_HAS_CUSTOM_CSS_ALREADY;
  if (route.params.result === ENTRA_ID_FEEDBACK_TYPES.ENTRA_STATUS_ERROR)
    return ENTRA_ID_FEEDBACK_MESSAGES.ENTRA_STATUS_ERROR;
  if (
    route.params.result ===
    ENTRA_ID_FEEDBACK_TYPES.ENTRA_STATUS_NO_ADMIN_CONSENT
  )
    return ENTRA_ID_FEEDBACK_MESSAGES.ENTRA_STATUS_NO_ADMIN_CONSENT;
  return ENTRA_ID_FEEDBACK_MESSAGES.ENTRA_STATUS_SUCCESS;
});

const variant = computed(() => {
  if (route.params.result === ENTRA_ID_FEEDBACK_TYPES.ENTRA_STATUS_ERROR)
    return 'danger';
  if (
    route.params.result ===
    ENTRA_ID_FEEDBACK_TYPES.ENTRA_STATUS_NO_ADMIN_CONSENT
  )
    return 'warning';
  if (route.params.result === ENTRA_ID_FEEDBACK_TYPES.ENTRA_STATUS_SUCCESS)
    return 'success';
  return 'info';
});

const closeWindow = () => {
  window.close();
};
</script>

<style></style>
