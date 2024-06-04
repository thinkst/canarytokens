<template>
  <div
    v-if="!isManualFlow"
    class="flex flex-col gap-16 md:flex-row"
  >
    <a
      class="relative border flex-1 group flex flex-col px-24 py-24 bg-white rounded-xl top-[0px] shadow-solid-shadow-grey border-grey-200 items-center duration-100 ease-in-out hover:border-green hover:shadow-solid-shadow-green-500-md hover:top-[-0.2em]"
      :href="automaticLink"
      target="_blank"
    >
      <font-awesome-icon
        icon="robot"
        aria-hidden="true"
        class="h-[2rem] text-green-200 mb-[16px]"
      />
      <span class="font-semibold text-grey-500">Automatic flow</span>
      <span class="text-sm text-grey-400"
        >You give us access to manage your Entra setup</span
      >
    </a>
    <button
      class="relative border flex-1 group flex flex-col px-24 py-24 bg-white rounded-xl top-[0px] shadow-solid-shadow-grey border-grey-200 items-center duration-100 ease-in-out hover:border-green hover:shadow-solid-shadow-green-500-md hover:top-[-0.2em]"
      @click.stop="handleFlowType"
    >
      <font-awesome-icon
        icon="hands"
        aria-hidden="true"
        class="h-[2rem] text-green-200 mb-[16px]"
      />
      <span class="font-semibold text-grey-500">Manual flow</span>
      <span class="text-sm text-grey-400"
        >You insert the token manually yourself</span
      >
    </button>
  </div>

  <div
    v-if="isManualFlow"
    class="relative text-center"
  >
    <div>
      <h3 class="font-semibold text-center text-md text-grey-800">
        Manual Flow
      </h3>
      <button
        class="text-sm font-semibold text-center md:absolute text-grey-300 hover:text-green-500 top-4 md:left-[0px]"
        @click.stop="handleFlowType"
      >
        <font-awesome-icon
          icon="arrow-left"
          aria-hidden="true"
        />
        Not sure? Go Back
      </button>
      <ul class="flex flex-col gap-[16px] text-center my-16">
        <li class="py-16 bg-white rounded-lg">
          <p class="mb-8 text-sm">Download the necessary CSS:</p>
          <BaseButton
            variant="secondary"
            @click="handleDownloadCSSAzureEntraID"
            >Download CSS</BaseButton
          >
        </li>
        <font-awesome-icon
          class="text-sm font-semibold text-green-500"
          icon="arrow-down"
          aria-hidden="true"
        />
        <li class="py-16 bg-white rounded-lg">
          <p class="mb-8 text-sm">
            Navigate to your Entra ID login customisation page.
          </p>
          <BaseButton
            variant="secondary"
            class="inline-block"
            target="_blank"
            href="https://entra.microsoft.com/#view/Microsoft_AAD_UsersAndTenants/CompanyBrandingWizard.ReactView/isDefault~/true/companyBrandingToEdit~/%7B%22id%22%3A%220%22%2C%22backgroundColor%22%3A%22%2340c223%22%2C%22backgroundImageRelativeUrl%22%3Anull%2C%22bannerLogoRelativeUrl%22%3Anull%2C%22cdnList%22%3A%5B%22aadcdn.msftauthimages.net%22%2C%22aadcdn.msauthimages.net%22%5D%2C%22customAccountResetCredentialsUrl%22%3Anull%2C%22customCannotAccessYourAccountText%22%3Anull%2C%22customCannotAccessYourAccountUrl%22%3Anull%2C%22customForgotMyPasswordText%22%3Anull%2C%22customPrivacyAndCookiesText%22%3Anull%2C%22customPrivacyAndCookiesUrl%22%3Anull%2C%22customResetItNowText%22%3Anull%2C%22customTermsOfUseText%22%3Anull%2C%22customTermsOfUseUrl%22%3Anull%2C%22faviconRelativeUrl%22%3Anull%2C%22customCSSRelativeUrl%22%3Anull%2C%22headerBackgroundColor%22%3Anull%2C%22signInPageText%22%3A%22%22%2C%22squareLogoRelativeUrl%22%3Anull%2C%22squareLogoDarkRelativeUrl%22%3Anull%2C%22usernameHintText%22%3A%22%22%2C%22headerLogoRelativeUrl%22%3Anull%2C%22loginPageTextVisibilitySettings%22%3A%7B%22hideCannotAccessYourAccount%22%3Anull%2C%22hideAccountResetCredentials%22%3Afalse%2C%22hideTermsOfUse%22%3Afalse%2C%22hidePrivacyAndCookies%22%3Afalse%2C%22hideForgotMyPassword%22%3Anull%2C%22hideResetItNow%22%3Anull%7D%2C%22contentCustomization%22%3A%7B%22adminConsentRelativeUrl%22%3Anull%2C%22attributeCollectionRelativeUrl%22%3Anull%2C%22registrationCampaignRelativeUrl%22%3Anull%2C%22conditionalAccessRelativeUrl%22%3Anull%2C%22adminConsent%22%3A%5B%5D%2C%22attributeCollection%22%3A%5B%5D%2C%22registrationCampaign%22%3A%5B%5D%2C%22conditionalAccess%22%3A%5B%5D%7D%2C%22loginPageLayoutConfiguration%22%3A%7B%22layoutTemplateType%22%3A%22default%22%2C%22isHeaderShown%22%3Afalse%2C%22isFooterShown%22%3Atrue%7D%7D/configuredLocales~/%5B%22en-US%22%5D"
            >Go to your page</BaseButton
          >
        </li>
        <font-awesome-icon
          class="text-sm font-semibold text-green-500"
          icon="arrow-down"
          aria-hidden="true"
        />
        <li class="py-16 bg-white rounded-lg">
          <p class="p-16 text-sm">
            Choose <span class="font-bold">Layout</span>, scroll down to
            <span class="font-bold">Custom CSS</span>, click
            <span class="font-bold">Browse</span> and choose the downloaded CSS
            from the first step.
          </p>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { downloadAsset } from '@/api/main';

type AzureEntraDataType = {
  auth: string;
  token: string;
  client_id: string;
  css: string;
};

const props = defineProps<{
  tokenData: AzureEntraDataType;
}>();

const isManualFlow = ref(false);

const automaticLink = computed(() => {
  const state = escape(btoa(`${props.tokenData?.css}`));
  const redirect = `${window.location.origin}/azure_css_landing`;
  return `https://login.microsoftonline.com/common/adminconsent?client_id=${props.tokenData.client_id}&state=${state}&redirect_uri=${redirect}`;
});

function handleFlowType() {
  isManualFlow.value = !isManualFlow.value;
}

async function handleDownloadCSSAzureEntraID() {
  const params = {
    fmt: 'cssclonedsite',
    auth: props.tokenData?.auth,
    token: props.tokenData?.token,
  };

  try {
    const res = await downloadAsset(params);
    window.location.href = res.request.responseURL;
  } catch (err) {
    console.log(err, 'File download failed');
  } finally {
    console.log('Donwload ready');
  }
}
</script>
