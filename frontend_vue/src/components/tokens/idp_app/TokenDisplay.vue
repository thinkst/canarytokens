<template>
  <div class="flex flex-col gap-16">
    <div class="flex flex-col items-center justify-center gap-8">
      <BaseLabelArrow
        id="idp-app-img"
        :arrow-word-position="3"
        label="App Icon"
        arrow-variant="one"
        class="text-center"
      />
      <BaseDownloadIconButton
        :url="getImageUrl(`idp_icons/${appType}.png`)"
      />
    </div>

    <BaseCodeSnippet
      lang="javascript"
      label="App Name"
      is-single-line
      :code="IDP_OPTIONS.find(o => o.value === appType)?.label ?? ''"
    ></BaseCodeSnippet>
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
      docs</a>.
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
