<template>
  <div class="flex flex-col gap-16">
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
  </div>
  <BaseMessageBox
    variant="info"
    class="mt-32"
    >For setup instructions for Entra ID and Okta, head over to our
    <a
      style="text-decoration: underline"
      href="https://docs.canarytokens.org/guide/idp-app-token.html"
      target="_blank"
    >
      docs</a
    >.
  </BaseMessageBox>
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
