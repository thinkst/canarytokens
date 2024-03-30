<template>
  <base-code-snippet
    lang="javascript"
    label="Somethin"
    :code="newTokenData.token_url"
  ></base-code-snippet>
</template>

<script setup lang="ts">
type webActiveType = {
  token: string;
  hostname: string;
  token_url: string;
  auth_token: string;
  email: string;
  webhook_url: '';
  url_components: string[];
  error: string;
  error_message: string;
  Url: string;
  token_type: string;
};

defineProps<{
  newTokenData: webActiveType;
}>();
</script>
