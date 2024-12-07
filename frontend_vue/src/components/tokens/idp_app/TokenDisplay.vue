<template>
  <BaseMessageBox
    variant="info"
    class="mt-6 mb-16"
    >We have custom instructions for
    <a style="text-decoration: underline" target="_blank"
      href="https://docs.canarytokens.org/guide/idp-app-token.html#deploying-to-azure"
    >
      Entra ID</a> and
    <a style="text-decoration: underline" target="_blank"
      href="https://docs.canarytokens.org/guide/idp-app-token.html#deploying-to-okta"
    >
      Okta</a>, in our
    <a style="text-decoration: underline" target="_blank"
      href="https://docs.canarytokens.org/guide/idp-app-token.html"
    >
      docs</a>.
  </BaseMessageBox>
  <div class="flex flex-col gap-16">
    <BaseCodeSnippet
      lang="javascript"
      label="ACS / Relay State URL"
      is-single-line
      :code="tokenUrl"
    ></BaseCodeSnippet>
    <BaseCodeSnippet
      lang="javascript"
      label="Entity ID"
      is-single-line
      :code="entityId"
    ></BaseCodeSnippet>

    <div class="flex flex-col">
      <label
        id="app_icon"
        class="inline-block mb-8 text-grey-500"
        for="app_name"
        >App Details</label
      >
      <div class="flex flex-row justify-center gap-16">
        <BaseDownloadIconButton
          :url="getImageUrl(`idp_icons/${appType}.png`)"
          alt="App Icon"
        />
        <BaseCodeSnippet
          id="app_name"
          lang="javascript"
          class="w-full"
          is-single-line
          :code="IDP_OPTIONS.find((o) => o.value === appType)?.label ?? ''"
        ></BaseCodeSnippet>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { IDP_OPTIONS } from '@/components/constants';
import getImageUrl from '@/utils/getImageUrl';

defineProps<{
  tokenUrl: string;
  entityId: string;
  appType: string;
}>();
</script>
