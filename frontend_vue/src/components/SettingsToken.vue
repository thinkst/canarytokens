<template>
  <div class="flex flex-col gap-24">
    enabledEmailAlert: {{ enabledEmailAlert }}
    <BaseSwitch
      v-if="hasEmailAlert"
      id="email-alert"
      :v-model="enabledEmailAlert"
      label="Email alerts"
      :helper-message="tokenBackendResponse.canarydrop.alert_email_recipient"
      :loading="loadingEmailAlert"
      @click.prevent="
        handleChangeSetting(
          ENABLE_SETTINGS_TYPE.EMAIL as EnableSettingsOptionType,
          !enabledEmailAlert
        )
      "
    />
    <BaseSwitch
      v-if="hasWebhookAlert"
      id="webhook-alert"
      v-model="enabledWebhookAlert"
      label="Webhook reporting"
      :helper-message="props.tokenBackendResponse.canarydrop.alert_webhook_url"
      @change.stop="
        handleChangeSetting(
          ENABLE_SETTINGS_TYPE.WEB_HOOK as EnableSettingsOptionType,
          enabledWebhookAlert
        )
      "
    />
    <BaseSwitch
      v-if="hasBrowserScan"
      id="browser-alert"
      v-model="enabledBrowserScan"
      label="Browser scanner"
      helper-message="Runs Javascript fingerprinting when the token is browsed"
      @change.stop="
        handleChangeSetting(
          ENABLE_SETTINGS_TYPE.BROWSER_SCANNER as EnableSettingsOptionType,
          enabledBrowserScan
        )
      "
    />
    <BaseSwitch
      v-if="hasCustomImage"
      id="custom-image"
      v-model="enabledCustomImage"
      label="Custom web image"
      helper-message="Serve your alternative image"
      @change.stop="
        handleChangeSetting(
          ENABLE_SETTINGS_TYPE.WEB_IMAGE as EnableSettingsOptionType,
          enabledCustomImage
        )
      "
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';
import { settingsToken } from '@/api/main';
import type { SettingsTokenType, EnableSettingsOptionType } from '@/api/main';
import { ENABLE_SETTINGS_TYPE, TOKENS_TYPE } from '@/components/constants';

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

const hasEmailAlert = ref(
  props.tokenBackendResponse.canarydrop.alert_email_recipient
);
const hasWebhookAlert = ref(
  props.tokenBackendResponse.canarydrop.alert_webhook_url
);
const hasBrowserScan = ref(isSupportBrowserScan());
const hasCustomImage = ref(isSupportCustomImage());

const enabledEmailAlert = ref(false);
const enabledWebhookAlert = ref(false);
const enabledBrowserScan = ref(false);
const enabledCustomImage = ref(false);

const loadingEmailAlert = ref(false);

onMounted(() => {
  enabledEmailAlert.value =
    (hasEmailAlert.value &&
      props.tokenBackendResponse.canarydrop?.alert_email_enabled) ||
    false;
  enabledWebhookAlert.value =
    (hasWebhookAlert.value &&
      props.tokenBackendResponse.canarydrop?.alert_webhook_enabled) ||
    false;
  enabledBrowserScan.value =
    (hasBrowserScan.value &&
      props.tokenBackendResponse.canarydrop?.browser_scanner_enabled) ||
    false;
  enabledCustomImage.value =
    (hasCustomImage.value &&
      props.tokenBackendResponse.canarydrop?.web_image_enabled) ||
    false;
});

// backend requires a string 'on' or 'off' to enable/disable feature
function convertBooleanToValue(boolean: boolean): string {
  return boolean ? 'on' : 'off';
}

async function handleChangeSetting(
  settingType: EnableSettingsOptionType,
  isSettingTypeEnabled: boolean
) {
  const params = {
    value: convertBooleanToValue(isSettingTypeEnabled),
    token: props.tokenBackendResponse.canarydrop.canarytoken._value,
    auth: props.tokenBackendResponse.canarydrop.auth,
    setting: settingType,
  };

  loadingEmailAlert.value = true;
  console.log(enabledEmailAlert.value);

  try {
    await settingsToken(params as SettingsTokenType);
    enabledEmailAlert.value = !enabledEmailAlert.value;
  } catch (err) {
    console.log(err, 'error!');
    // enabledEmailAlert.value = !enabledEmailAlert.value;
  } finally {
    loadingEmailAlert.value = false;
    console.log('setting updated!');
  }

  // settingsToken(params as SettingsTokenType)
  //   .then(() => {
  //     enabledEmailAlert.value = !enabledEmailAlert.value;
  //   })
  //   .catch((err) => {
  //     enabledEmailAlert.value = !enabledEmailAlert.value;
  //     console.log(err, 'error!');
  //   })
  //   .finally(() => {
  //     loadingEmailAlert.value = false;
  //     console.log('setting updated!');
  //   });
}
</script>
