<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseFormTextField
      id="redirect_url"
      type="text"
      placeholder="https://www.example.com"
      label="Redirect URL"
      full-width
      required
    />
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="For instance: URL within Dropbox"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
</script>
