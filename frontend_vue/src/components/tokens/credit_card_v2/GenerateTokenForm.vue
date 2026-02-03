<template>
  <div v-if="loadingCreditCardDetails">
    <vue-turnstile
      class="flex align-center justify-center mt-24"
      :site-key="cloudflareSiteKey"
      theme="light"
      v-model="getQuotaCloudflareResponse"
      />
  </div>
  <div v-else-if="errorGettingCreditCardDetails">
    <base-message-box
        class="mt-24" variant="danger"
        :message="`Oops, something went wrong!`" />
  </div>
  <div v-else>
    <div v-if="cards_quota > 0">
      <GenerateTokenSettingsNotifications
        memo-helper-example="Credit Card placed in payment card database" />

      <BaseFormTextField
        v-show="false"
        id="cf_turnstile_response"
        type="text"
        placeholder="cf_turnstile_response"
        label="cf_turnstile_response"
        full-width
        :value="generateTokenCloudflareResponse"
        required
      />

      <vue-turnstile
        class="flex align-center justify-center mt-24"
        :site-key="cloudflareSiteKey"
        theme="light"
        v-model="generateTokenCloudflareResponse"
        />
    </div>
    <div v-else>
      <base-message-box
        class="mt-24" variant="warning"
        :message="`Sorry, we've run out of Credit Card tokens!\n New cards are added to the pool everyday so please try again later.`" />
    </div>
  </div>
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
import VueTurnstile from 'vue-turnstile';
import { ref, watch } from 'vue';
import type { Ref } from 'vue';
import { getCreditCardDetails } from '@/api/main.ts';

const getQuotaCloudflareResponse: Ref<string> = ref('');
const generateTokenCloudflareResponse: Ref<string> = ref('');
const cloudflareSiteKey: string = import.meta.env.VITE_CLOUDFLARE_TURNSTILE_SITE_KEY;

const loadingCreditCardDetails = ref(true);
const errorGettingCreditCardDetails = ref(false);
const cards_quota: Ref<number> = ref(0);

async function getCCDetails() {
  loadingCreditCardDetails.value = true;
  errorGettingCreditCardDetails.value = false;
  try {
    const result = await getCreditCardDetails(getQuotaCloudflareResponse.value);
    cards_quota.value = result.data.quota;
  } catch (err) {
    errorGettingCreditCardDetails.value = true;
    console.log(err, 'Getting CC Details failed.');
  } finally {
    loadingCreditCardDetails.value = false;
  }
}

watch(getQuotaCloudflareResponse, () => {
  if (getQuotaCloudflareResponse.value !== '') {
    getCCDetails();
  }
});
</script>
