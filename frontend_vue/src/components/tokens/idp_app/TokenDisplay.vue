<template>
  <div class="flex flex-col gap-16">
    <base-code-snippet
      lang="javascript"
      label="ACS / Relay State URL"
      is-single-line
      :code="tokenUrl"
    ></base-code-snippet>
    <base-code-snippet
      lang="javascript"
      label="Entity ID"
      is-single-line
      :code="entityId"
    ></base-code-snippet>
  </div>
  <BaseMessageBox
    variant="info"
    class="mt-32"
    >For setup instructions for Entra ID and Okta, head over to our
    <a
      style="text-decoration: underline"
      href="https://docs.canarytokens.org/guide/idp-app-token.html"
    >
      docs
    </a>
  </BaseMessageBox>
</template>

<script setup lang="ts">
defineProps<{
  tokenUrl: string;
  entityId: string;
}>();
</script>
