<template>
  <base-code-snippet
    lang="javascript"
    :code="newTokenData.token_type"
  ></base-code-snippet>
</template>

<script setup lang="ts">
type dnsActiveType = {
  token_type: 'dns';
  memo: 'Reminder note when this token is triggered';
  email: 'username@domain.com';
  webhook_url: 'https://slack.com/api/api.test';
};

defineProps<{
  newTokenData: dnsActiveType;
}>();
</script>
