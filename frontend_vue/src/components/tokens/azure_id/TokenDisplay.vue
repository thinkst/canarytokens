<template>
  <base-code-snippet
    lang="json"
    label="JSON config"
    :code="CertificateTokenCode"
    multiline
    custom-height="13rem"
  ></base-code-snippet>
  <base-button
    class="mt-16"
    @click="handleDownloadAzureCertificateFile"
    >Download Azure Certificate</base-button
  >
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { downloadAsset } from '@/api/main';

type AzureIDDataType = {
  auth: string;
  token: string;
  appId: string;
  displayName: string;
  fileWithCertAndPrivateKey: string;
  tenant: string;
};

const props = defineProps<{
  tokenData: AzureIDDataType;
}>();

const CertificateTokenCode = ref(`{
  "appId": "${props.tokenData.appId}",
  "displayName" : "${props.tokenData.displayName}",
  "fileWithCertAndPrivateKey": "${props.tokenData.fileWithCertAndPrivateKey}",
  "password": null,
  "tenant": "${props.tokenData.tenant}"
  }`);

async function handleDownloadAzureCertificateFile() {
  const params = {
    fmt: 'azure_id',
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
