<template>
  <div class="flex flex-col gap-24">
    <BaseSwitch
      v-if="hasEmailAlert"
      id="email-alert"
      v-model="settingRefs.EMAIL"
      label="Email alerts"
      :helper-message="tokenBackendResponse.canarydrop.alert_email_recipient"
      :loading="loadingRefs.EMAIL"
      :has-error="errorRefs.EMAIL"
      :error-message="errorMessage"
      @click.prevent="
        handleChangeSetting(
          SETTINGS_TYPE.EMAIL as keyof typeof SETTINGS_TYPE,
          !settingRefs.EMAIL
        )
      "
    />
    <BaseSwitch
      v-if="hasWebhookAlert"
      id="webhook-alert"
      v-model="settingRefs.WEB_HOOK"
      label="Webhook reporting"
      :helper-message="props.tokenBackendResponse.canarydrop.alert_webhook_url"
      :loading="loadingRefs.WEB_HOOK"
      :has-error="errorRefs.WEB_HOOK"
      :error-message="errorMessage"
      @click.prevent="
        handleChangeSetting(
          SETTINGS_TYPE.WEB_HOOK as keyof typeof SETTINGS_TYPE,
          !settingRefs.WEB_HOOK
        )
      "
    />
    <BaseSwitch
      v-if="hasBrowserScan"
      id="browser-alert"
      v-model="settingRefs.BROWSER_SCANNER"
      label="Browser scanner"
      helper-message="Runs Javascript fingerprinting when the token is browsed"
      :loading="loadingRefs.BROWSER_SCANNER"
      :has-error="errorRefs.BROWSER_SCANNER"
      :error-message="errorMessage"
      @click.prevent="
        handleChangeSetting(
          SETTINGS_TYPE.BROWSER_SCANNER as keyof typeof SETTINGS_TYPE,
          !settingRefs.BROWSER_SCANNER
        )
      "
    />
    <BaseSwitch
      v-if="hasCustomImage"
      id="custom-image"
      v-model="settingRefs.WEB_IMAGE"
      label="Custom web image"
      helper-message="Serve your alternative image"
      :loading="loadingRefs.WEB_IMAGE"
      :has-error="errorRefs.WEB_IMAGE"
      :error-message="errorMessage"
      @click.prevent="
        handleChangeSetting(
          SETTINGS_TYPE.WEB_IMAGE as keyof typeof SETTINGS_TYPE,
          !settingRefs.WEB_IMAGE
        )
      "
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';
import { settingsToken } from '@/api/main';
import type { SettingsTokenType } from '@/api/main';
import {
  SETTINGS_TYPE,
  UPDATE_SETTINGS_BACKEND_TYPE,
  GET_SETTINGS_BACKEND_TYPE,
  TOKENS_TYPE,
} from '@/components/constants';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

function isSupportBrowserScan() {
  return (
    props.tokenBackendResponse.canarydrop.type === TOKENS_TYPE.WEB_BUG ||
    props.tokenBackendResponse.canarydrop.type === TOKENS_TYPE.WEB_IMAGE
  );
}

function isSupportCustomImage() {
  return props.tokenBackendResponse.canarydrop.type === TOKENS_TYPE.WEB_IMAGE;
}

// Check which settings are available for this Token
const hasEmailAlert = ref(
  props.tokenBackendResponse.canarydrop.alert_email_recipient
);
const hasWebhookAlert = ref(
  props.tokenBackendResponse.canarydrop.alert_webhook_url
);
const hasBrowserScan = ref(isSupportBrowserScan());
const hasCustomImage = ref(isSupportCustomImage());

// State of each setting type
const settingRefs = ref({
  [SETTINGS_TYPE.EMAIL]: false,
  [SETTINGS_TYPE.WEB_HOOK]: false,
  [SETTINGS_TYPE.BROWSER_SCANNER]: false,
  [SETTINGS_TYPE.WEB_IMAGE]: false,
});

// Handle Loading for Switch Component during settings change
const loadingRefs = ref({
  [SETTINGS_TYPE.EMAIL]: false,
  [SETTINGS_TYPE.WEB_HOOK]: false,
  [SETTINGS_TYPE.BROWSER_SCANNER]: false,
  [SETTINGS_TYPE.WEB_IMAGE]: false,
});

// Handle Errors for Switch Component during settings change
const errorRefs = ref({
  [SETTINGS_TYPE.EMAIL]: false,
  [SETTINGS_TYPE.WEB_HOOK]: false,
  [SETTINGS_TYPE.BROWSER_SCANNER]: false,
  [SETTINGS_TYPE.WEB_IMAGE]: false,
});

const errorMessage = 'An error occurred. Please try again.';

onMounted(() => {
  // Set initial state
  // by getting the settings from the backend response
  Object.keys(SETTINGS_TYPE).forEach((key) => {
    const backendPropertyName =
      GET_SETTINGS_BACKEND_TYPE[key as keyof typeof SETTINGS_TYPE];

    settingRefs.value[key] = Boolean(
      props.tokenBackendResponse.canarydrop[backendPropertyName]
    );

    loadingRefs.value[key] = false;
    errorRefs.value[key] = false;
  });
});

// backend requires a string 'on' or 'off' to enable/disable feature
function convertBooleanToValue(boolean: boolean): string {
  return boolean ? 'on' : 'off';
}

async function handleChangeSetting(
  settingType: keyof typeof SETTINGS_TYPE,
  isSettingTypeEnabled: boolean
) {
  const params = {
    value: convertBooleanToValue(isSettingTypeEnabled),
    token: props.tokenBackendResponse.canarydrop.canarytoken._value,
    auth: props.tokenBackendResponse.canarydrop.auth,
    setting: UPDATE_SETTINGS_BACKEND_TYPE[settingType],
  };

  // Remove all previous errors
  Object.keys(errorRefs.value).forEach((key) => {
    errorRefs.value[key] = false;
  });

  loadingRefs.value[settingType] = true;

  try {
    const res = await settingsToken(params as SettingsTokenType);
    if (res.status === 200) {
      settingRefs.value[settingType] = isSettingTypeEnabled;
    } else {
      console.log('Error:', res.data.detail);
      errorRefs.value[settingType] = true;
    }
  } catch (err) {
    console.log(err, 'error!');
    errorRefs.value[settingType] = true;
  } finally {
    loadingRefs.value[settingType] = false;
  }
}
</script>
