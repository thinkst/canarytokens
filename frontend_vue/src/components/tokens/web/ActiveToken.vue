<template>
  <base-code-snippet
    lang="javascript"
    label="URL token"
    :code="newTokenData.token_url"
  ></base-code-snippet>
  <p class="mt-24">
    Remember, it gets triggered whenever someone requests the URL.
  </p>
  <p class="mt-24">
    If the URL is requested as an image (e.g. &lt;img src="" /&gt;) then a 1x1
    image is served. If the URL is surfed in a browser then a blank page is
    served with fingerprinting Javascript.
  </p>
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
