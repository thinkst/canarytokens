<template>
  <BaseGenerateTokenSettings setting-type="Additional">
    <BaseFormTextField
      id="redirect_url"
      type="text"
      placeholder="Redirect URL"
      label="Redirect URL"
      full-width
      required
    />
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="URL within Dropbox"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
</script>
