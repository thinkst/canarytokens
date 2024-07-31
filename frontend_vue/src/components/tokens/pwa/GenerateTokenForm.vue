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
      id="icon_location"
      type="text"
      placeholder="/resources/pwa_password_512.png"
      label="Icon location (optional)"
      helper-message="Location of the icon, this will be replaced with a grid of choices. currently we have '/resources/pwa_password_512.png', '/resources/pwa_gallery_512.png', and '/resources/pwa_fnb_512.png'"
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
