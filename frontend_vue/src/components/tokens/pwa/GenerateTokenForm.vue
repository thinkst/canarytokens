<template>
    <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseFormTextField
      id="app_name"
      type="text"
      placeholder="Passwords"
      label="App Name (optional)"
      helper-message="Something an attacker would like to open that matches your icon"
      full-width
      required
    />
    <BaseFormTextField
      id="icon"
      type="text"
      placeholder="password"
      label="Icon location (optional)"
      helper-message="The icon to be used, this will be replaced with a grid of choices. currently we have 'password', 'gallery', and 'fnb'"
      full-width
      required
    />
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="Fake Password Manager app on Alice's phone"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
</script>
