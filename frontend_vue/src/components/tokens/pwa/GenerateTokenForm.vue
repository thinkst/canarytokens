<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseFormTextField
      id="app_name"
      type="text"
      placeholder="E.g. Password Manager"
      label="App name (optional)"
      full-width
      class="text-center"
    />
    <BaseFormImageSelect
      id="app_icon"
      label="Select App icon (optional)"
      :options="[
        { value: 'fnb', url: `${getImageUrl('pwa_fnb.png')}` },
        { value: 'gallery', url: `${getImageUrl('pwa_gallery.png')}` },
        { value: 'password', url: `${getImageUrl('pwa_password.png')}` },
      ]"
    />
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="Fake Password Manager app on Alice's phone"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
import getImageUrl from '@/utils/getImageUrl';
</script>
